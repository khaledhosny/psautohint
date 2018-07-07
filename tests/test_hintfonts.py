from __future__ import print_function, division, absolute_import

import glob
from os.path import basename
import pytest

from fontTools.misc.xmlWriter import XMLWriter
from fontTools.ttLib import TTFont
from psautohint.autohint import ACOptions, hintFiles

from .differ import main as differ
from . import DATA_DIR


class Options(ACOptions):
    def __init__(self, inpath, outpath):
        super(Options, self).__init__()
        self.inputPaths = [inpath]
        self.outputPaths = [outpath]
        self.hintAll = True
        self.verbose = False


@pytest.mark.parametrize("ufo", glob.glob("%s/*/*/font.ufo" % DATA_DIR))
def test_ufo(ufo, tmpdir):
    out = str(tmpdir / basename(ufo))
    options = Options(ufo, out)
    hintFiles(options)

    assert differ([ufo, out])


@pytest.mark.parametrize("otf", glob.glob("%s/*/*/font.otf" % DATA_DIR))
def test_otf(otf, tmpdir):
    out = str(tmpdir / basename(otf))
    options = Options(otf, out)
    hintFiles(options)

    for path in (otf, out):
        font = TTFont(path)
        assert "CFF " in font
        writer = XMLWriter(path + ".xml")
        font["CFF "].toXML(writer, font)
        del writer
        del font

    assert differ([otf + ".xml", out + ".xml"])