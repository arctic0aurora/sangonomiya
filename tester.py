from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *
from benchmark import *

import characters.pyro.arlecchino

import numpy as np
import argparse


def test_arlecchino(args=None):
    characters.pyro.arlecchino.ArlecchinoV0.bond_sequence = characters.pyro.arlecchino.bond_simulation(vapor_rate=1.0, print_sequence=False)   
    arlecchino = characters.pyro.arlecchino.ArlecchinoV0(constellation=0, weapon='sand', virtual_artefact='whimsy', understanding='mult')
    arlecchino_path = './artefacts/test'
    optim = Optimizer(arlecchino, arlecchino_path, team=['yelan', 'zhongli-instructor', 'benette-noblesse'], args=[])
    optim.optimize_artifacts(requirement=arlecchino.requirement)
    optim.print_options(counts=1)

if __name__ == '__main__':
    test_arlecchino()
