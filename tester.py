from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *
from benchmark import *

import characters.pyro.arlecchino as arlecchino

import numpy as np
import argparse


def test_arlecchino(args=None):
    arlecchino.ArlecchinoV3.bond_sequence = arlecchino.bond_simulation(axis=arlecchino.ArlecchinoV3.axis_maxima, vapor_rate=1.0, print_sequence=False)   
    _arlecchino = arlecchino.ArlecchinoV3(constellation=0, weapon='sand', virtual_artefact='whimsy')
    arlecchino_path = './artefacts/test'
    optim = Optimizer(_arlecchino, arlecchino_path, team=['yelan', 'zhongli-instructor', 'benette-noblesse'], args=[])
    optim.optimize_artifacts(requirement=_arlecchino.requirement)
    optim.print_options(counts=1, print_level=0)

if __name__ == '__main__':
    test_arlecchino()
