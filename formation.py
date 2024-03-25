from reaction import *

import functools

# standard class for damage
@functools.total_ordering
class Composite:
    def __init__(self, exp=0, ncrit=0, crit=0):
        self.exp = exp      # expected damage
        self.ncrit = ncrit  # non-crit damage
        self.crit = crit    # crit damage
    
    # calculations
    def __add__(self, a):
        if isinstance(a, Composite):
            return Composite(self.exp+a.exp, self.ncrit+a.ncrit, self.crit+a.crit)
        else:
            return Composite(self.exp+a, self.ncrit+a, self.crit+a)
    
    def __iadd__(self, num):
        return Composite(self.exp+num, self.ncrit+num, self.crit+num)

    def __mul__(self, num):
        return Composite(self.exp*num, self.ncrit*num, self.crit*num)
    
    def __imul__(self, num):
        return Composite(self.exp*num, self.ncrit*num, self.crit*num)

    def __str__(self):
        return "(exp: {:.1f}, crit: {:.1f}, non-crit: {:.1f})".format(self.exp, self.crit, self.ncrit)

    # lesser than
    def __lt__(self, a):
        return (self.exp < a.exp)
    

def calc_damage(mult, atk, cr, cd, bns, res, rdf=0, quill=0, reaction={}, enemy_level=90):
    if cr > 100:
        cr = 100
    mult, cr, cd, bns = mult*0.01, cr*0.01, cd*0.01, bns*0.01
    resist = resist_factor(res)
    defence = defence_factor(rdf, 90, enemy_level)

    amplification = 1
    intensification = 0
    if reaction:
        for rea, em in reaction.items():
            if rea == 'amplify':
                amplification *= amplify.amplify(em)
            elif rea == 'reverse_amplify':
                amplification *= amplify.reverse_amplify(em)
            elif rea == 'aggrevate':
                intensification += intensify.aggravate(em)
            elif rea == 'spread':
                intensification += intensify.spread(em)

    noncrit = (mult*atk+quill+intensification) * (1+bns) * amplification * resist * defence
    crit = noncrit * (1+cd)
    exp = noncrit * (1+cr*cd)

    return Composite(exp, noncrit, crit)

def resist_factor(res):
    if res > 0:
        return (100-res)*0.01
    else:
        return (100-0.5*res)*0.01

def defence_factor(rdf, player_level=90, enemy_level=90):
    # return (player_level+100) / (player_level+enemy_level+200)
    return (player_level+100) / ((player_level+100) + (enemy_level+100)*(1+0.01*rdf))