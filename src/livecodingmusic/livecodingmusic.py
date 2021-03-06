import time
from datetime import datetime
from collections import deque, OrderedDict
import random
import json
import re
import math
import sys
import os

from icecream import ic
from pythonosc import udp_client

osc = udp_client.SimpleUDPClient("127.0.0.1", 57120)

db_notes = [
    ["C", "B#", "Bs"],
    ["Db", "C#", "Cs"],
    ["D"],
    ["Eb", "D#", "Ds"],
    ["E", "Fb"],
    ["F", "E#", "Es"],
    ["F#", "Gb", "Fs"],
    ["G"],
    ["G#", "Ab", "Gs"],
    ["A"],
    ["A#", "Bb", "As"],
    ["B", "Cb"],
]

## helper functions
def get_note(s):
    note_name = ""
    note_index = 0
    longest = 0
    for i, notes in enumerate(db_notes):
        for _, note in enumerate(notes):
            if len(note) < longest:
                continue
            if s.upper().startswith(note.upper()):
                longest = len(note)
                note_name = note
                note_index = i
    if longest == 0:
        raise ValueError
    return note_name, note_index


def note2midi(note_user):
    note_user = note_user.replace(" ", "").upper()
    notes = []
    last_octave = 4
    while len(note_user) > 0:
        note_name, note_index = get_note(note_user)
        note_user = note_user[len(note_name) :]
        try:
            octave = re.findall(r"[0-9]+", note_user)[0]
            note_user = note_user[len(octave) :]
            octave = int(octave)
            last_octave = octave
        except:
            octave = last_octave
        notes.append(note_index + 12 * octave)
    return notes


print(note2midi("eb4"))


def chord2midi(chord_user):
    db_chords = json.loads(
        """{
  "4": ["1P 4P 7m 10m", "quartal"],
  "64": ["5P 8P 10M"],
  "5": ["1P 5P"],
  "M": ["1P 3M 5P", "Major", "", "maj"],
  "M#5": ["1P 3M 5A", "augmented", "maj#5", "Maj#5", "+", "aug"],
  "M#5add9": ["1P 3M 5A 9M", "+add9"],
  "M13": ["1P 3M 5P 7M 9M 13M", "maj13", "Maj13"],
  "M13#11": ["1P 3M 5P 7M 9M 11A 13M","maj13#11", "Maj13#11", "M13+4", "M13#4"],
  "M6": ["1P 3M 5P 13M", "6"],
  "M6#11": ["1P 3M 5P 6M 11A", "M6b5", "6#11", "6b5"],
  "M69": ["1P 3M 5P 6M 9M", "69"],
  "M69#11": ["1P 3M 5P 6M 9M 11A"],
  "M7#11": ["1P 3M 5P 7M 11A", "maj7#11", "Maj7#11", "M7+4", "M7#4"],
  "M7#5": ["1P 3M 5A 7M", "maj7#5", "Maj7#5", "maj9#5", "M7+"],
  "M7#5sus4": ["1P 4P 5A 7M"],
  "M7#9#11": ["1P 3M 5P 7M 9A 11A"],
  "M7add13": ["1P 3M 5P 6M 7M 9M"],
  "M7b5": ["1P 3M 5d 7M"],
  "M7b6": ["1P 3M 6m 7M"],
  "M7b9": ["1P 3M 5P 7M 9m"],
  "M7sus4": ["1P 4P 5P 7M"],
  "M9": ["1P 3M 5P 7M 9M", "maj9", "Maj9"],
  "M9#11": ["1P 3M 5P 7M 9M 11A", "maj9#11", "Maj9#11", "M9+4", "M9#4"],
  "M9#5": ["1P 3M 5A 7M 9M", "Maj9#5"],
  "M9#5sus4": ["1P 4P 5A 7M 9M"],
  "M9b5": ["1P 3M 5d 7M 9M"],
  "M9sus4": ["1P 4P 5P 7M 9M"],
  "Madd9": ["1P 3M 5P 9M", "2", "add9", "add2"],
  "Maj7": ["1P 3M 5P 7M", "maj7", "M7"],
  "Mb5": ["1P 3M 5d"],
  "Mb6": ["1P 3M 13m"],
  "Msus2": ["1P 2M 5P", "add9no3", "sus2"],
  "Msus4": ["1P 4P 5P", "sus", "sus4"],
  "Maddb9": ["1P 3M 5P 9m"],
  "7": ["1P 3M 5P 7m", "Dominant", "Dom"],
  "9": ["1P 3M 5P 7m 9M", "79"],
  "11": ["1P 5P 7m 9M 11P"],
  "13": ["1P 3M 5P 7m 9M 13M", "13_"],
  "11b9": ["1P 5P 7m 9m 11P"],
  "13#11": ["1P 3M 5P 7m 9M 11A 13M", "13+4", "13#4"],
  "13#9": ["1P 3M 5P 7m 9A 13M", "13#9_"],
  "13#9#11": ["1P 3M 5P 7m 9A 11A 13M"],
  "13b5": ["1P 3M 5d 6M 7m 9M"],
  "13b9": ["1P 3M 5P 7m 9m 13M"],
  "13b9#11": ["1P 3M 5P 7m 9m 11A 13M"],
  "13no5": ["1P 3M 7m 9M 13M"],
  "13sus4": ["1P 4P 5P 7m 9M 13M", "13sus"],
  "69#11": ["1P 3M 5P 6M 9M 11A"],
  "7#11": ["1P 3M 5P 7m 11A", "7+4", "7#4", "7#11_", "7#4_"],
  "7#11b13": ["1P 3M 5P 7m 11A 13m", "7b5b13"],
  "7#5": ["1P 3M 5A 7m", "+7", "7aug", "aug7"],
  "7#5#9": ["1P 3M 5A 7m 9A", "7alt", "7#5#9_", "7#9b13_"],
  "7#5b9": ["1P 3M 5A 7m 9m"],
  "7#5b9#11": ["1P 3M 5A 7m 9m 11A"],
  "7#5sus4": ["1P 4P 5A 7m"],
  "7#9": ["1P 3M 5P 7m 9A", "7#9_"],
  "7#9#11": ["1P 3M 5P 7m 9A 11A", "7b5#9"],
  "7#9#11b13": ["1P 3M 5P 7m 9A 11A 13m"],
  "7#9b13": ["1P 3M 5P 7m 9A 13m"],
  "7add6": ["1P 3M 5P 7m 13M", "67", "7add13"],
  "7b13": ["1P 3M 7m 13m"],
  "7b5": ["1P 3M 5d 7m"],
  "7b6": ["1P 3M 5P 6m 7m"],
  "7b9": ["1P 3M 5P 7m 9m"],
  "7b9#11": ["1P 3M 5P 7m 9m 11A", "7b5b9"],
  "7b9#9": ["1P 3M 5P 7m 9m 9A"],
  "7b9b13": ["1P 3M 5P 7m 9m 13m"],
  "7b9b13#11": ["1P 3M 5P 7m 9m 11A 13m", "7b9#11b13", "7b5b9b13"],
  "7no5": ["1P 3M 7m"],
  "7sus4": ["1P 4P 5P 7m", "7sus"],
  "7sus4b9": ["1P 4P 5P 7m 9m","susb9", "7susb9", "7b9sus", "7b9sus4", "phryg"],
  "7sus4b9b13": ["1P 4P 5P 7m 9m 13m", "7b9b13sus4"],
  "9#11": ["1P 3M 5P 7m 9M 11A", "9+4", "9#4", "9#11_", "9#4_"],
  "9#11b13": ["1P 3M 5P 7m 9M 11A 13m", "9b5b13"],
  "9#5": ["1P 3M 5A 7m 9M", "9+"],
  "9#5#11": ["1P 3M 5A 7m 9M 11A"],
  "9b13": ["1P 3M 7m 9M 13m"],
  "9b5": ["1P 3M 5d 7m 9M"],
  "9no5": ["1P 3M 7m 9M"],
  "9sus4": ["1P 4P 5P 7m 9M", "9sus"],
  "m": ["1P 3m 5P"],
  "m#5": ["1P 3m 5A", "m+", "mb6"],
  "m11": ["1P 3m 5P 7m 9M 11P", "_11"],
  "m11A 5": ["1P 3m 6m 7m 9M 11P"],
  "m11b5": ["1P 3m 7m 12d 2M 4P", "h11", "_11b5"],
  "m13": ["1P 3m 5P 7m 9M 11P 13M", "_13"],
  "m6": ["1P 3m 4P 5P 13M", "_6"],
  "m69": ["1P 3m 5P 6M 9M", "_69"],
  "m7": ["1P 3m 5P 7m", "minor7", "_", "_7"],
  "m7#5": ["1P 3m 6m 7m"],
  "m7add11": ["1P 3m 5P 7m 11P", "m7add4"],
  "m7b5": ["1P 3m 5d 7m", "half-diminished", "h7", "_7b5"],
  "m9": ["1P 3m 5P 7m 9M", "_9"],
  "m9#5": ["1P 3m 6m 7m 9M"],
  "m9b5": ["1P 3m 7m 12d 2M", "h9", "-9b5"],
  "mMaj7": ["1P 3m 5P 7M", "mM7", "_M7"],
  "mMaj7b6": ["1P 3m 5P 6m 7M", "mM7b6"],
  "mM9": ["1P 3m 5P 7M 9M", "mMaj9", "-M9"],
  "mM9b6": ["1P 3m 5P 6m 7M 9M", "mMaj9b6"],
  "mb6M7": ["1P 3m 6m 7M"],
  "mb6b9": ["1P 3m 6m 9m"],
  "o": ["1P 3m 5d", "mb5", "dim"],
  "o7": ["1P 3m 5d 13M", "diminished", "m6b5", "dim7"],
  "o7M7": ["1P 3m 5d 6M 7M"],
  "oM7": ["1P 3m 5d 7M"],
  "sus24": ["1P 2M 4P 5P", "sus4add9"],
  "+add#9": ["1P 3M 5A 9A"],
  "madd4": ["1P 3m 4P 5P"],
  "madd9": ["1P 3m 5P 9M"]
}
"""
    )

    def get_chord_type(s):
        longest = 0
        chord_type = ""
        chord_interval = ""
        for c1 in db_chords:
            chord_types = [c1]
            interval = ""
            for i, v in enumerate(db_chords[c1]):
                if i == 0:
                    interval = v
                else:
                    chord_types.append(v)
            for _, ct in enumerate(chord_types):
                if len(ct) < longest:
                    continue
                if s.startswith(ct):
                    chord_type = ct
                    longest = len(ct)
                    chord_interval = interval
        if longest == 0:
            chord_type = "M"
            chord_interval = db_chords["M"][0]
        return chord_type, chord_interval

    def interval_to_notes(s):
        notes_interval = []
        whole_note_semitones = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]
        for _, interval_str in enumerate(s.split()):
            num = int(re.findall(r"[0-9]+", interval_str)[0])
            intv = re.findall(r"[A-Za-z]+", interval_str)[0]
            semitones = whole_note_semitones[num - 1]
            if intv == "A":
                semitones += 1
            elif intv == "m":
                semitones -= 1
            notes_interval.append(semitones)
        return notes_interval

    octave = 4
    foo = chord_user.split(":")
    chord_user = foo[0]
    if len(foo) == 2:
        octave = int(foo[1])

    chord_inversion = chord_user.split("/")
    chord_user = chord_inversion[0]

    note_name, note_index = get_note(chord_user)
    ic(note_name, note_index)

    chord_user_without_note = chord_user[len(note_name) :]
    ic(chord_user_without_note)

    chord_type, chord_interval = get_chord_type(chord_user_without_note)
    ic(chord_type, chord_interval)

    notes_interval = interval_to_notes(chord_interval)
    ic(notes_interval)

    if len(chord_inversion) == 2:
        _, inversion_index = get_note(chord_inversion[1])
        found_inversion = False
        notes_interval2 = []
        for _, v in enumerate(notes_interval):
            if v == inversion_index:
                found_inversion = True
            if not found_inversion:
                v += 12
            notes_interval2.append(v)
        notes_interval2 = sorted(notes_interval2)
        if found_inversion:
            notes_interval = notes_interval2
    ic(notes_interval)

    for i, v in enumerate(notes_interval):
        notes_interval[i] = v + (12 * octave) + note_index

    ic(notes_interval)
    return notes_interval


# er - euclidean rhythms
# returns table of 0's and 1's
def er(steps, pulses, shift=0):
    steps = int(steps)
    pulses = int(pulses)
    if pulses > steps:
        raise ValueError
    pattern = []
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)

    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)
        else:
            for i in range(0, counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)

    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]
    pattern = deque(pattern)
    pattern.rotate(shift)
    pattern = list(pattern)
    return pattern


# patch definitions

sc_sample_basic = {
    "sample": "",
    "db": -20,
    "attack": 0,
    "decay": 0.05,
    "pan": 0,
    "lpf": 16000,
    "reverb": -24,
    "delay": -24,
    "rate": 1,
    "rateLag": 0,
    "start": 0,
    "end": 1,
    "reset": 0,
    "loops": 2,
    "note": 0,  # not used
}

sc_synthy_basic = {
    "db": 0,
    "note": 20,
    "attack": 0,
    "decay": 1,
    "pan": 0,
    "lpf": 8000,
    "reverb": -24,
    "delay": -24,
    "sub": 0,
}
sc_piano_basic = {
    "db": 0,
    "note": 20,
    "attack": 0,
    "decay": 2,
    "pan": 0,
    "lpf": 8000,
    "reverb": -24,
    "delay": -24,
}
sc_bass_basic = {
    "db": 0,
    "note": 20,
    "attack": 0.01,
    "decay": 2,
    "pan": 0,
    "lpf": 8000,
    "reverb": -24,
    "delay": -24,
}


sc_fm_kick = {
    "db": 10,
    "note": 20,
    "attack": 0,
    "decay": 1,
    "pan": 0,
    "lpf": 320,
    "reverb": -24,
    "delay": -24,
    "mRatio": 0.4,
    "cRatio": 1.5,
    "index": 0.5,
    "iScale": 0.5,
    "cAtk": 4,
    "cRel": -8,
    "noise": -7,
    "natk": 0.01,
    "nrel": 0.6,
    "eqFreq": 134,
    "eqDB": 8,
}
sc_fm_hh = {
    "db": -30,
    "note": 20,
    "attack": 0,
    "decay": 0.1,
    "pan": 0,
    "lpf": 16000,
    "reverb": -18,
    "delay": -36,
    "mRatio": 1.5,
    "cRatio": 45.9,
    "index": 100,
    "iScale": 1,
    "cAtk": 4,
    "cRel": -8,
    "noise": 11,
    "natk": 0.01,
    "nrel": 0.11,
    "eqFreq": 1200,
    "eqDB": 0,
}

sc_fm_pad = {
    "db": -20,
    "note": 20,
    "attack": 2,
    "decay": 2,
    "pan": 0,
    "lpf": 16000,
    "reverb": -15,
    "delay": -15,
    "mRatio": 2,
    "cRatio": 1,
    "index": 1,
    "iScale": 4,
    "cAtk": 0,
    "cRel": 0,
    "noise": -96,
    "natk": 0.01,
    "nrel": 0.01,
    "eqFreq": 800,
    "eqDB": 10,
}


class Engine:
    params = []

    def __init__(self, name, patch="basic"):
        self.name = name
        self.patches = {}
        if name == "fm":
            self.params = [
                "db",
                "note",
                "attack",
                "decay",
                "pan",
                "lpf",
                "reverb",
                "delay",
                "mRatio",
                "cRatio",
                "index",
                "iScale",
                "cAtk",
                "cRel",
                "noise",
                "natk",
                "nrel",
                "eqFreq",
                "eqDB",
            ]
            self.patches['basic'] = sc_fm_kick.copy()
            self.patches['kick'] = sc_fm_kick.copy()
            self.patches['hh'] = sc_fm_hh.copy()
            self.patches['pad'] = sc_fm_pad.copy()
        elif name == "sample":
            self.params = [
                "sample",
                "db",
                "attack",
                "decay",
                "pan",
                "lpf",
                "reverb",
                "delay",
                "rate",
                "rateLag",
                "start",
                "end",
                "reset",
                "loops",
            ]
            self.patches['basic'] = sc_sample_basic.copy()
        elif name == "synthy":
            self.params = [
                "db",
                "note",
                "attack",
                "decay",
                "pan",
                "lpf",
                "reverb",
                "delay",
                "sub",
            ]
            self.patches['basic'] = sc_synthy_basic.copy()
        elif name == "piano":
            self.params = [
                "db",
                "note",
                "attack",
                "decay",
                "pan",
                "lpf",
                "reverb",
                "delay",
            ]
            self.patches['basic'] = sc_piano_basic.copy()
        elif name == "bass":
            self.params = [
                "db",
                "note",
                "attack",
                "decay",
                "pan",
                "lpf",
                "reverb",
                "delay",
            ]
            self.patches['basic'] = sc_bass_basic.copy()
        else:
            raise ValueError("no engine " + name + " exists")
        self.patch = self.patches[patch]

    def set(self, k, v):
        if k == "sample":
            v = os.path.abspath(v)
        self.patch[k] = v

    def play(self, notes_send=[]):
        patch = self.patch
        if "notes" not in patch.keys():
            patch["notes"] = [patch["note"]]
        if len(notes_send) > 0:
            patch["notes"] = notes_send
        patch["notes"] = sorted(patch["notes"])
        for i, note in enumerate(patch["notes"]):
            parm_send = []
            patch["note"] = note
            if "sub" in patch:
                if i == 0:
                    patch["sub"] = patch["sub"] + 1
                else:
                    patch["sub"] = 0
            for parm in self.params:
                parm_send.append(patch[parm])
            osc.send_message("/" + self.name, parm_send)


# https://stackoverflow.com/questions/51389691/how-can-i-do-a-precise-metronome
def metronome(fn, bpm):
    step = -1
    tempo, steps_per_beat = bpm()
    delay = d = 60 / tempo / steps_per_beat
    prev = time.perf_counter()
    while True:
        step += 1
        fn(step)
        t = time.perf_counter()
        tempo, steps_per_beat = bpm()
        delta = t - prev - (60 / tempo / steps_per_beat)
        # print('{:+.9f}'.format(delta))
        d -= delta
        prev = t
        if d > 0:
            time.sleep(d)


recording = False


def record(on):
    global recording
    if on and not recording:
        osc.send_message("/record", 1)
        recording = True
    elif not on and recording:
        osc.send_message("/record", 0)
        recording = False


## user stuff


# def bpm():
#     return 135


# def sample_drums(step):
#     if random.random() < 0.75:
#         return
#     sample = "/home/zns/Downloads/livecoding.py/120_8.wav"
#     sample_beats = 8
#     s = step % (sample_beats * 4)
#     start = s / (sample_beats * 4)
#     end = 1
#     reset = start
#     rate = bpm() / 120
#     patch = sc_sample.basic.copy()
#     patch["rate"] = rate
#     patch["sample"] = sample
#     patch["start"] = start
#     patch["reset"] = reset
#     patch["end"] = end
#     patch["db"] = -15
#     patch["pan"] = -0.3
#     patch["loops"] = 4
#     patch["reverb"] = -96
#     patch["delay"] = -96
#     patch["lpf"] = 15000
#     if random.random() < 0.005:
#         patch["rate"] = patch["rate"] * -1
#     if random.random() < 0.1:
#         patch["lpf"] = random.random() * 2000 + 200
#     if random.random() < 0.05:
#         patch["end"] = start + 1 / random.choice([48, 64, 72, 96])
#         patch["reset"] = start
#         patch["lpf"] = 2000
#         patch["loops"] = 128
#     sc_sample(patch)


# def fm_kick(step):
#     fname = sys._getframe().f_code.co_name
#     if not hasattr(globals()[fname], "v"):
#         globals()[fname].v = 0
#     v = globals()[fname].v
#     notes = [15, 23]
#     e = [er(16, 3, 2), er(16, 2, 0)][v]
#     s = step % len(e)
#     if not e[s]:
#         return
#     globals()[fname].v = 1 - v
#     patch = sc_fm.kick.copy()
#     patch["note"] = notes[v]
#     patch["db"] = 10
#     patch["lpf"] = 320
#     patch["reverb"] = -27
#     sc_fm(patch)


# def fm_hh(step):
#     fname = sys._getframe().f_code.co_name
#     if not hasattr(globals()[fname], "v"):
#         globals()[fname].v = 0
#     v = globals()[fname].v
#     notes = [65, 53]
#     e = [er(16, 4, 2), er(16, 3, 0)][v]
#     s = step % len(e)
#     if not e[s]:
#         return
#     globals()[fname].v = 1 - v
#     patch = sc_fm.hh.copy()
#     patch["note"] = notes[v]
#     patch["decay"] = 0.05
#     patch["db"] = -24
#     patch["delay"] = -15
#     patch["reverb"] = -25
#     ic(step, s)
#     sc_fm(patch)


# def fm_pad(step):
#     fname = sys._getframe().f_code.co_name
#     if not hasattr(globals()[fname], "pulse"):
#         globals()[fname].pulse = -1
#     e = er(32, 1, 0)
#     s = step % len(e)
#     if not e[s]:
#         return
#     chords = ["C/G", "Em7/D:4", "Am7:4", "F:4"]
#     globals()[fname].pulse = (globals()[fname].pulse + 1) % len(chords)
#     pulse = globals()[fname].pulse
#     patch = sc_fm.pad.copy()
#     patch["attack"] = 60 / bpm() * 4
#     patch["decay"] = 60 / bpm() * 2
#     patch["reverb"] = -5
#     patch["db"] = -30
#     patch["notes"] = chord2midi(chords[pulse])
#     sc_fm(patch)


# def synthy_pad(step):
#     fname = sys._getframe().f_code.co_name
#     if not hasattr(globals()[fname], "pulse"):
#         globals()[fname].pulse = -1
#     e = er(32, 1, 0)
#     s = step % len(e)
#     if not e[s]:
#         return
#     chords = ["C:5", "Em7/D:5", "Am7/C:5", "F/C:5"]
#     globals()[fname].pulse = (globals()[fname].pulse + 1) % len(chords)
#     pulse = globals()[fname].pulse
#     patch = sc_synthy.pad.copy()
#     patch["attack"] = 60 / bpm() * 4
#     patch["decay"] = 60 / bpm() * 4
#     patch["reverb"] = -5
#     patch["delay"] = 0
#     patch["db"] = 0
#     patch["sub"] = 1
#     patch["notes"] = chord2midi(chords[pulse])
#     sc_synthy(patch)


# def main(step):
#     synthy_pad(step)
#     # sample_drums(step)
#     # fm_pad(step)
#     fm_hh(step)
#     # fm_kick(step)
#     pass
