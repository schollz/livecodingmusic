import random
import sys

sys.path.insert(0, "src")

from livecodingmusic.livecodingmusic import Engine
from livecodingmusic.livecodingmusic import chord2midi
from livecodingmusic.livecodingmusic import note2midi
from livecodingmusic.livecodingmusic import er
from livecodingmusic.livecodingmusic import metronome
from icecream import ic


def sample(step):
    if step % 16 != 0:
        return
    if random.random() < 0.1:
        return

    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = -1
    globals()[fname].v = (globals()[fname].v + 1) % 3
    v = globals()[fname].v
    sample = "SO_MM_115_vocalsynth_cashmere_wet_Am__beats35_bpm115.wav"
    e = Engine("sample")
    e.set("loops", 1)
    e.set("sample", sample)
    e.set("rate", 1)
    ic(v, sample)
    e.set("reset", v * 12 / 35)
    e.set("start", v * 12 / 35)
    e.set("reverb", -15)
    e.set("db", -20)
    e.play()


def sample2(step):
    if step % 64 != 0:
        return

    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = -1
    globals()[fname].v = (globals()[fname].v + 1) % 4
    v = globals()[fname].v

    sample = "SO_MM_115_vocalsynth_cerulean_wet_Am__beats38_bpm115.wav"
    e = Engine("sample")
    e.set("sample", sample)
    e.set("loops", 1)
    e.set("rate", 1)
    e.set("db", -15)
    e.set("lpf", 16000)

    e.set("reset", 0.3 + (0.1 * v))
    e.set("end", 0.3 + (0.1 * v))
    e.set("start", 0)
    e.play()


def sample_drums(step):
    if random.random() < 0.5:
        return
    e = Engine("sample")
    e.set("sample", "120_8.wav")
    sample_beats = 8
    sample_tempo = 120
    e.set("sample", "loop_amen1_bpm174.wav")
    sample_beats = 16
    sample_tempo = 174

    # update the rate to keep in tempo
    tempo, steps_per_beat = bpm()
    e.set("rate", tempo / sample_tempo)

    # update the position to match
    s = step % (sample_beats * steps_per_beat)
    start = s / (sample_beats * steps_per_beat)
    e.set("pan", -0)
    e.set("db", -15)
    e.set("loops", 2)
    e.set("start", start)
    e.set("reset", start)
    e.set("end", 1)
    e.set("lpf", 16000)
    if random.random() < 0.05:
        e.set("rate", -tempo / 120 * 1)
    if random.random() < 0.1:
        e.set("lpf", random.random() * 2000 + 200)
    if random.random() < 0.05:
        e.set("end", start + 1 / random.choice([48, 64, 72, 96]))
        e.set("loops", 128)
        e.set("lpf", 2000)

    e.play()


def kick(step):
    if step % 8 != 0:
        return
    e = Engine("fm", "kick")
    e.set("reverb", -30)
    e.set("db", 40)
    e.play()


def hh(step):
    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = 0
    globals()[fname].v = 1 - globals()[fname].v
    v = globals()[fname].v

    ers = [er(16, 7, 0), er(16, 5, 0)]
    if ers[v][step % 16] != 1:
        return

    e = Engine("fm", "hh")
    e.set("reverb", -40)
    e.set("db", -25)
    e.play()


def pad(step):
    if step % 16 != 0:
        return
    # define some chords
    chords = ["Am7", "Cmaj7", "Am7", "Cmaj7", "Am7", "Cmaj7", "F/C", "Em/B"]

    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = -1
    globals()[fname].v = (globals()[fname].v + 1) % len(chords)
    v = globals()[fname].v

    e = Engine("synthy")
    e.set("attack", 1.8)
    e.set("decay", 0.1)
    e.set("reverb", -15)
    e.set("db", -10)
    e.set("lpf", 1620)
    e.play(chord2midi(chords[v]))


def notes(step):
    if er(16, 6, 1)[step % 16] == 0:
        return
    notes = ["a6", "c6", "e6", "d6", "e7", "a5"]

    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = -1
    globals()[fname].v = (globals()[fname].v + 1) % len(notes)
    v = globals()[fname].v

    e = Engine("piano")
    e.set("attack", 0.01)
    e.set("decay", 1.5)
    e.set("db", -30)
    e.set("lpf", 1600)
    e.play(note2midi(notes[v]))


def notes2(step):
    if er(16, 2, 1)[step % 16] == 0:
        return
    notes = ["c5", "b4", "a3", "e4", "f5", "g5"]

    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = -1
    globals()[fname].v = (globals()[fname].v + 1) % len(notes)
    v = globals()[fname].v

    e = Engine("piano")
    e.set("attack", 0.01)
    e.set("decay", 1.5)
    e.set("db", -20)
    e.set("lpf", 18100)
    e.set("delay", -5)
    e.set("sub", 0.5)
    e.play(note2midi(notes[v]))


def bass(step):
    if step % 16 != 0:
        return
    # define some chords
    notes = ["a2", "c2", "a2", "c2", "a2", "c2", "f2", "e2"]

    # save state
    fname = sys._getframe().f_code.co_name
    if not hasattr(globals()[fname], "v"):
        globals()[fname].v = -1
    globals()[fname].v = (globals()[fname].v + 1) % len(notes)
    v = globals()[fname].v

    e = Engine("bass")
    e.set("attack", 0.01)
    e.set("decay", 2.5)
    e.set("db", 0)
    e.play(note2midi(notes[v]))


def loop(step):
    # bass(step)
    # pad(step)
    # kick(step)
    # hh(step)
    # sample_drums(step)
    # sample(step)
    # sample2(step)
    # notes(step)
    # notes2(step)
    pass


def bpm():
    # return tempo, steps per beat
    return 115, 4


if __name__ == "__main__":
    metronome(loop, bpm)
