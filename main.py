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
    mode = args.mode
    character = args.chara

    if mode == 'benchmark':
        return
    
    if character == 'ayaka':
        ayaka = characters.ayaka.Ayaka(weapon='mistsplitter', cryo_weight=1, frozen_weight=0.5)
        ayaka_path = './artefacts/ayaka'
        optim = Optimizer(ayaka, ayaka_path, team=['kazuha', 'kokomi', 'shenhe'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=ayaka.requirement)
        optim.print_options(counts=args.option_cnt)
    elif character == 'furina':
        characters.furina.Furina.fanfare_sequence = characters.furina.fanfare_simulation()
        furina = characters.furina.Furina(weapon='misugiri', rejoice_weight=0.8, duckweed_weight=0.5)
        furina_path = './artefacts/furina'
        optim = Optimizer(furina, furina_path, team=['kazuha', 'kokomi', 'yelan'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=furina.requirement)
        optim.print_options(counts=args.option_cnt)
    elif character == 'albedo':
        albedo = characters.geo.albedo.Albedo(weapon='spindle')
        albedo_path = './artefacts/geo'
        optim = Optimizer(albedo, albedo_path, team=['noelle', 'chiori', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=albedo.requirement)
        optim.print_options(counts=args.option_cnt)
    elif character == 'noelle':
        noelle = characters.geo.noelle.Noelle(weapon='skyward')
        noelle_path = './artefacts/geo'
        optim = Optimizer(noelle, noelle_path, team=['albedo', 'chiori', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=noelle.requirement)
        optim.print_options(counts=args.option_cnt)
    elif character == 'chiori':
        chiori = characters.geo.chiori.Chiori(weapon='misugiri')
        chiori_path = './artefacts/geo'
        optim = Optimizer(chiori, chiori_path, team=['noelle', 'gorou', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=chiori.requirement)
        optim.print_options(counts=args.option_cnt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sangonomiya')
    parser.add_argument('--mode', type=str, default='optim', help='mode')
    parser.add_argument('--chara', type=str, default='ayaka', help='character')
    parser.add_argument('--option-cnt', type=int, default=5, help='optimal options')
    main(parser.parse_args())
