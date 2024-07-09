from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *
from benchmark import *

import characters.ayaka as ayaka
import characters.furina as furina
import characters.geo.noelle as noelle
import characters.geo.chiori as chiori
import characters.geo.albedo as albedo

import numpy as np
import argparse


def main(args):
    mode = args.mode
    character = args.chara
    # benchmark mode
    if mode == 'benchmark':
        optim = BenchmarkOptimizer(character)
        optim.optimize_benchmark()
        optim.print_result()
        return
    # optimization mode
    if character == 'ayaka':
        _ayaka = ayaka.Ayaka(weapon='mistsplitter', cryo_weight=1, frozen_weight=0.5)
        ayaka_path = './artefacts/ayaka'
        optim = Optimizer(_ayaka, ayaka_path, team=['kazuha', 'kokomi', 'shenhe-favonius'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=_ayaka.requirement)
    elif character == 'furina':
        furina.Furina.fanfare_sequence = furina.fanfare_simulation()
        _furina = furina.Furina(weapon='tranquil', rejoice_weight=0.8, duckweed_weight=0.6)
        furina_path = './artefacts/furina'
        optim = Optimizer(_furina, furina_path, team=['lynette', 'ayato', 'sigewinne'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=_furina.requirement)
    elif character == 'albedo':
        _albedo = albedo.Albedo(weapon='spindle')
        albedo_path = './artefacts/geo'
        optim = Optimizer(_albedo, albedo_path, team=['noelle', 'chiori', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=_albedo.requirement)
    elif character == 'noelle':
        _noelle = noelle.Noelle(weapon='redhorn')
        noelle_path = './artefacts/geo'
        optim = Optimizer(_noelle, noelle_path, team=['albedo', 'gorou', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=_noelle.requirement)
    elif character == 'chiori':
        _chiori = chiori.Chiori(weapon='misugiri')
        chiori_path = './artefacts/geo'
        optim = Optimizer(_chiori, chiori_path, team=['noelle', 'gorou', 'furina'], args=['recharge_thres'])
        optim.optimize_artifacts(requirement=_chiori.requirement)
    # print info
    optim.print_options(counts=args.option_cnt, print_level=args.print_level)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sangonomiya')
    parser.add_argument('--mode', type=str, default='optim', help='mode')
    parser.add_argument('--chara', type=str, default='ayaka', help='character')
    parser.add_argument('--option-cnt', type=int, default=3, help='options num')
    parser.add_argument('--print-level', type=int, default=0, help='print level')
    main(parser.parse_args())
