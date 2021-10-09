import unittest
import pytest

from livecodingmusic.livecodingmusic import chord2midi
from livecodingmusic.livecodingmusic import note2midi
from livecodingmusic.livecodingmusic import er


def test_chord2midi():
    assert chord2midi("Am7") == [57, 60, 64, 67]
    assert note2midi("a4 b5") == [57, 71]
    assert er(4, 2, 1) == [0, 1, 0, 1]
