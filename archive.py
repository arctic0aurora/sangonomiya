import numpy as np

attribute_names = {
        'H': 'HP%',
        'h': 'HP',
        'A': 'Attack%',
        'a': 'Attack',
        'D': 'Defence%',
        'd': 'Defence',
        'hp': 'HP',
        'atk': 'Attack',
        'df': 'Defence',
        'spd': 'Speed',
        'cr': 'Crit Rate',
        'cd': 'Crit Damage',
        'rcg': 'Recharge',
        'bns': 'Bonus',
        'em': 'Elemental Mastery',
        'anemo': 'Anemo',
        'hydro': 'Hydro',
        'cryo': 'Cryo',
        'pyro': 'Pyro',
        'electro': 'Electro',
        'geo': 'Geo',
        'dendro': 'Dendro',
        'physical': 'Physical',
        'quantum': 'Quantum',
        'imaginary': 'Imaginary',
    }

genshin_slots = [
    'flower', 'plume', 'hourglass', 'goblet', 'circlet'
]

genshin_substats = [
    'cr', 'cd', 'rcg', 'em', 'H', 'A', 'D', 'h', 'a', 'd'
]

starrail_slots = [
    'head', 'hand', 'body', 'feet', 'sphere', 'rope'
]

# print masks
all_mask = [key for key in attribute_names]
atk_mask = ['A', 'a', 'cr', 'cd', 'bns']

# sort keys
def default_sort_key(result):
    return result.feature.exp


