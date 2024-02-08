from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import characters.ayaka
import characters.furina
import characters.geo.noelle
import characters.geo.chiori
import characters.geo.albedo

import numpy as np
import argparse


def main(args):
    character = args.chara
    if character == 'ayaka':
        ayaka = characters.ayaka.Ayaka(weapon='mistsplitter', cryo_weight=1, frozen_weight=0.5)
        ayaka_path = './artefacts/ayaka'
        optim = Optimizer(ayaka, ayaka_path, team=['kazuha', 'kokomi', 'shenhe'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=ayaka.requirement)
        optim.print_options()
    elif character == 'furina':
        furina = characters.furina.Furina(weapon='jade', fanfare_weight=0.5, duckweed_weight=0.33)
        furina_path = './artefacts/furina'
        optim = Optimizer(furina, furina_path, team=['kazuha', 'kokomi', 'xingqiu'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=furina.requirement)
        optim.print_options()
    elif character == 'albedo':
        albedo = characters.geo.albedo.Albedo(weapon='spindle')
        albedo_path = './artefacts/geo'
        optim = Optimizer(albedo, albedo_path, team=['noelle', 'chiori', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=albedo.requirement)
        optim.print_options()
    elif character == 'noelle':
        noelle = characters.geo.noelle.Noelle(weapon='skyward')
        noelle_path = './artefacts/geo'
        optim = Optimizer(noelle, noelle_path, team=['albedo', 'chiori', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=noelle.requirement)
        optim.print_options()
    elif character == 'chiori':
        chiori = characters.geo.chiori.Chiori(weapon='yuraku')
        chiori_path = './artefacts/geo'
        optim = Optimizer(chiori, chiori_path, team=['albedo', 'gorou', 'zhongli'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=chiori.requirement)
        optim.print_options()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sangonomiya')
    parser.add_argument('--chara', type=str, default='ayaka', help='character')
    parser.add_argument('--option-cnt', type=int, default=10, help='optimal options')
    main(parser.parse_args())
