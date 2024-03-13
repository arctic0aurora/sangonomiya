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
    characters.pyro.arlecchino.ArlecchinoV0.bond_sequence = characters.pyro.arlecchino.bond_simulation()   
    arlecchino = characters.pyro.arlecchino.ArlecchinoV0(weapon='crimson', virtual_artefact='bond')
    arlecchino_path = './artefacts/test'
    optim = Optimizer(arlecchino, arlecchino_path, team=['xingqiu', 'furina', 'benette-instructor'], args=[])
    optim.optimize_artifacts(requirement=arlecchino.requirement)
    optim.print_options(counts=1)

if __name__ == '__main__':
    test_arlecchino()
