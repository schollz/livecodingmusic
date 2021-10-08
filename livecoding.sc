(
Routine{
	s.reboot;
	5.wait;
	"adding reverb".postln;
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

	SynthDef("fm", {
		arg note=50, mRatio=1, cRatio=1,
		index=1, iScale=5, cAtk=4, cRel=(-4),
		db=(-10), atk=0.01, rel=3, pan=0,
		noise=0.0, natk=0.01, nrel=3,
		eqFreq=1200,eqDB=0,
		lpf=20000, diskout,
		out=0, fx=0, fxsend=(-25);
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
		Out.ar(fx, car * Clip.kr(fxsend.dbamp));
	}).add;

	s.sync;
	~busReverb = Bus.audio(s,2);
	s.sync;
	~synReverb=Synth("reverb",[\in,~busReverb],s);
	s.sync;


	~oscFM.free;
	~oscFM = OSCFunc({ arg msg, time, addr, recvPort;
		msg.postln;
		Synth(\fm, [
			\db, msg[1],
			\note, msg[2],
			\atk, msg[3],
			\rel, msg[4],
			\pan, msg[5],
			\lpf, msg[6],
			\fxsend, msg[7],
			\mRatio, msg[8],
			\cRatio, msg[9],
			\index, msg[10],
			\iScale, msg[11],
			\cAtk, msg[12],
			\cRel, msg[13],
			\noise, msg[14],
			\natk, msg[15],
			\nrel, msg[16],
			\eqFreq, msg[17],
			\eqDB, msg[18],
			\fx, ~busReverb,
		]);
	}, '/fm');
}.play;
)