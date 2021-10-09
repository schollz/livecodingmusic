(
// jackd -R -dalsa -dhw:1,0 -r 44100 -p256 -n3
Routine{
	s.reboot;
	s.waitForBoot({

		SynthDef("reverb", {
			arg in=0, out=0, dec=4, lpf=1500;
			var sig;
			sig = In.ar(in, 2).sum;
			sig = DelayN.ar(sig, 0.03, 0.03);
			sig = CombN.ar(sig, 0.1, {Rand(0.01,0.099)}!32, dec);
			sig = SplayAz.ar(2, sig);
			sig = LPF.ar(sig, lpf);
			5.do{sig = AllpassN.ar(sig, 0.1, {Rand(0.01,0.099)}!2, 3)};
			sig = LPF.ar(sig, lpf);
			sig = LeakDC.ar(sig);
			Out.ar(out, sig);
		}).add;

		s.sync;
		~busReverb = Bus.audio(s,2);
		s.sync;
		~synReverb=Synth.tail(s,"reverb",[\in,~busReverb]);
		s.sync;

		SynthDef("delay", {
			arg in=0, out=0, secondsPerBeat=0.03125,delayBeats=4,delayFeedback=0.05;
			var sig;
			sig = In.ar(in, 2);
			sig = CombC.ar(
				sig,
				2,
				secondsPerBeat*delayBeats,
				secondsPerBeat*delayBeats*LinLin.kr(delayFeedback,0,1,2,128),// delayFeedback should vary between 2 and 128
			);
			Out.ar(out, sig);
		}).add;

		s.sync;
		~busDelay = Bus.audio(s,2);
		s.sync;
		~synDelay=Synth.tail(s,"delay",[\in,~busDelay]);
		s.sync;

		SynthDef("fm", {
			arg note=50, mRatio=1, cRatio=1,
			index=1, iScale=5, cAtk=4, cRel=(-4),
			db=(-10), atk=0.01, rel=3, pan=0,
			noise=0.0, natk=0.01, nrel=3,
			eqFreq=1200,eqDB=0,
			lpf=20000, diskout,
			out=0, outReverb=0, sendReverb=(-25),
			outDelay=0, sendDelay=(-25);
			var car, mod, env, iEnv, amp;
			var freq=note.midicps;
			amp=Clip.kr(db.dbamp,0,4);

			//index of modulation
			iEnv = EnvGen.kr(
				Env(
					[index, index*iScale, index],
					[atk, rel],
					[cAtk, cRel]
				)
			);

			//amplitude envelope
			env = EnvGen.kr(Env.perc(atk,rel,curve:[cAtk,cRel]));

			// modulator/carrier
			mod = SinOsc.ar(freq * mRatio, mul:freq * mRatio * iEnv);
			car = SinOsc.ar(freq * cRatio + mod) * env;

			// add some chorus
			car=DelayC.ar(car, rrand(0.01,0.03), LFNoise1.kr(Rand(5,10),0.01,0.02)/15 );

			// add some noise
			car=car+(WhiteNoise.ar(noise.dbamp)*EnvGen.kr(Env.perc(natk,nrel)));

			// add some boost
			car=BPeakEQ.ar(car,eqFreq,0.5,eqDB);

			// low-pass filter
			car=LPF.ar(car,lpf);

			// panning
			car = Pan2.ar(car, pan);

			// scaling
			car = car * amp / 10;

			// kill the sound
			DetectSilence.ar(car,doneAction:2);

			//direct out/reverb send
			Out.ar(out, car);
			Out.ar(outReverb, car * Clip.kr(sendReverb.dbamp));
			Out.ar(outDelay, car * Clip.kr(sendDelay.dbamp));
		}).add;

		~oscfm.free;
		~oscfm=OSCFunc({ arg msg, time, addr, recvPort;
			msg.postln;
			Synth.head(s,\fm, [
				\db, msg[1],
				\note, msg[2],
				\atk, msg[3],
				\rel, msg[4],
				\pan, msg[5],
				\lpf, msg[6],
				\sendReverb, msg[7],
				\sendDelay, msg[8],
				\mRatio, msg[9],
				\cRatio, msg[10],
				\index, msg[11],
				\iScale, msg[12],
				\cAtk, msg[13],
				\cRel, msg[14],
				\noise, msg[15],
				\natk, msg[16],
				\nrel, msg[17],
				\eqFreq, msg[18],
				\eqDB, msg[19],
				\outReverb, ~busReverb,
				\outDelay, ~busDelay,
			]);
		}, '/fm');





		SynthDef("synthy", {
			arg note=50, db=(-10), atk=0.01, rel=3, pan=0,
			lpf=20000,sub=0,gate=1,
			out=0, outReverb=0, sendReverb=(-25),
			outDelay=0, sendDelay=(-25);
			var snd,env;
			var perturb1val,perturb2val;
			sub=Lag.kr(sub,1);
			snd=Pan2.ar(Pulse.ar((note-12).midicps,LinLin.kr(LFTri.kr(0.5),-1,1,0.2,0.8))/12*sub);
			snd=snd+Mix.ar({
				var snd2;
				snd2=SawDPW.ar(note.midicps);
				snd2=LPF.ar(snd2,LinExp.kr(SinOsc.kr(rrand(1/30,1/10),rrand(0,2*pi)),-1,1,2000,12000));
				snd2=DelayC.ar(snd2, rrand(0.01,0.03), LFNoise1.kr(Rand(5,10),0.01,0.02)/15 );
				Pan2.ar(snd2,VarLag.kr(LFNoise0.kr(1/3),3,warp:\sine))/12
			}!2);
			env=EnvGen.ar(Env.perc(atk,rel),gate,doneAction:2);
			snd=LPF.ar(snd,lpf);
			snd = snd * env * db.dbamp;
			Out.ar(out,snd);
			Out.ar(outReverb, snd * Clip.kr(sendReverb.dbamp));
			Out.ar(outDelay, snd * Clip.kr(sendDelay.dbamp));
		}).add;

		~oscsynthy.free;
		~oscsynth=OSCFunc({ arg msg, time, addr, recvPort;
			msg.postln;
			Synth.head(s,\synthy, [
				\db, msg[1],
				\note, msg[2],
				\atk, msg[3],
				\rel, msg[4],
				\pan, msg[5],
				\lpf, msg[6],
				\sendReverb, msg[7],
				\sendDelay, msg[8],
				\sub, msg[9],
				\outReverb, ~busReverb,
				\outDelay, ~busDelay,
			]);
		}, '/synthy');


		SynthDef("samplePlayer", {
			arg out=0, outReverb=0, sendReverb=(-96), outDelay=0, sendDelay=(-96),
			bufnum=0, rate=1, rateLag=0,start=0, end=1, reset=0, t_trig=1,
			loops=1, db=0, lpf=20000, atk=0,rel=0, pan=0;
			var snd,snd2,pos,pos2,frames,duration,env;
			var startA,endA,startB,endB,resetA,resetB,crossfade,aOrB;
			var amp=db.dbamp;

			// latch to change trigger between the two
			aOrB=ToggleFF.kr(t_trig);
			startA=Latch.kr(start,aOrB);
			endA=Latch.kr(end,aOrB);
			resetA=Latch.kr(reset,aOrB);
			startB=Latch.kr(start,1-aOrB);
			endB=Latch.kr(end,1-aOrB);
			resetB=Latch.kr(reset,1-aOrB);
			crossfade=Lag.ar(K2A.ar(aOrB),0.05);


			rate = Lag.kr(rate,rateLag);
			rate = rate*BufRateScale.kr(bufnum);
			frames = BufFrames.kr(bufnum);
			duration = frames*(end-start)/rate.abs/s.sampleRate*loops;

			// envelope to clamp looping
			env=EnvGen.ar(
				Env.new(
					levels: [0,1,1,0],
					times: [atk,duration-atk-rel,rel],
				),
				gate:t_trig,
			);

			pos=Phasor.ar(
				trig:aOrB,
				rate:rate,
				start:(((rate>0)*startA)+((rate<0)*endA))*frames,
				end:(((rate>0)*endA)+((rate<0)*startA))*frames,
				resetPos:(((rate>0)*resetA)+((rate<0)*endA))*frames,
			);
			snd=BufRd.ar(
				numChannels:2,
				bufnum:bufnum,
				phase:pos,
				interpolation:4,
			);

			// add a second reader
			pos2=Phasor.ar(
				trig:(1-aOrB),
				rate:rate,
				start:(((rate>0)*startB)+((rate<0)*endB))*frames,
				end:(((rate>0)*endB)+((rate<0)*startB))*frames,
				resetPos:(((rate>0)*resetB)+((rate<0)*endB))*frames,
			);
			snd2=BufRd.ar(
				numChannels:2,
				bufnum:bufnum,
				phase:pos2,
				interpolation:4,
			);

			snd=(crossfade*snd)+((1-crossfade)*snd2) * env * amp;

			DetectSilence.ar(snd,doneAction:2);

			snd=LPF.ar(snd,Lag.kr(lpf,2));

			snd=Balance2.ar(snd[0],snd[1],pan);

			Out.ar(out, snd);
			Out.ar(outReverb, snd * Clip.kr(sendReverb.dbamp));
			Out.ar(outDelay, snd * Clip.kr(sendDelay.dbamp));
		}).add;

		~samples=Dictionary.new;
		~samplesPlaying=Dictionary.new;

		~oscSample.free;
		~oscSample=OSCFunc({ arg msg, time, addr, recvPort;
			var sample=msg[1];
			msg.postln;
			if (~samples.at(sample)==nil,{
				~samples.put(sample,Buffer.read(s,sample));
			},{
				if (~samplesPlaying.at(sample)==nil,{
					~samplesPlaying.put(sample,
						Synth.head(s,\samplePlayer, [
							\db, msg[2],
							\atk, msg[3],
							\rel, msg[4],
							\pan, msg[5],
							\lpf, msg[6],
							\sendReverb, msg[7],
							\sendDelay, msg[8],
							\rate, msg[9],
							\rateLag, msg[10],
							\start, msg[11],
							\end, msg[12],
							\reset, msg[13],
							\loops, msg[14],
							\t_trig, 1,
							\bufnum, ~samples.at(sample),
							\outReverb, ~busReverb,
							\outDelay, ~busDelay,
						]).onFree({
							~samplesPlaying.removeAt(sample);
						});
					);
				},{
					~samplesPlaying.at(sample).set(
						\db, msg[2],
						\pan, msg[5],
						\lpf, msg[6],
						\sendReverb, msg[7],
						\sendDelay, msg[8],
						\rate, msg[9],
						\rateLag, msg[10],
						\start, msg[11],
						\end, msg[12],
						\reset, msg[13],
						\loops, msg[14],
						\t_trig, 1,
					);
				});
			});
		}, '/sample');

		"ready to listen to livecoding.py".postln;
	});

}.play;
)

s.record