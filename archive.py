class SangonomiyaArchive():
    # string constants
    # genshin
    genshin_panel = [
        'hp', 'atk', 'df', 'cr', 'cd', 'rcg', 'bns', 'em', 'anemo', 'cryo', 'hydro', 'pyro', 'electro', 'dendro', 'geo', 'physical'
    ]

    genshin_slots = [
        'flower', 'plume', 'hourglass', 'goblet', 'circlet'
    ]

    genshin_substats = [
        'cr', 'cd', 'rcg', 'em', 'H', 'A', 'D', 'h', 'a', 'd'
    ]

    # starrail
    starrail_panel = [
        'hp', 'atk', 'df', 'spd', 'cr', 'cd', 'rcg', 'bns', 'anemo', 'cryo', 'pyro', 'electro', 'physical', 'quantum', 'imaginary'
    ]

    starrail_slots = [
        'head', 'hand', 'body', 'feet', 'sphere', 'rope'
    ]

    # generic
    attr_name = {
        'H': 'hp%',
        'h': 'hp+',
        'A': 'atk%',
        'a': 'atk+',
        'D': 'def%',
        'd': 'def+',
        'hp': 'hp',
        'atk': 'attack',
        'df': 'defence',
        'spd': 'speed',
        'cr': 'crit_rate',
        'cd': 'crit_damage',
        'rcg': 'recharge',
        'bns': 'bonus',
        'em': 'elemental_mastery',
        'anemo': 'anemo',
        'hydro': 'hydro',
        'cryo': 'cryo',
        'pyro': 'pyro',
        'electro': 'electro',
        'geo': 'geo',
        'dendro': 'dendro',
        'physical': 'physical',
        'quantum': 'quantum',
        'imaginary': 'imaginary',
    }

    # sort keys
    def default_sort_key(result):
        return result.feature.exp


