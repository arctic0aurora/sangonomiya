from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Chiori(CharacterBase):
    def __init__(self, weapon='misugiri'):
        self.name = 'Chiori'
        self.weapon = weapon
        chiori_base = {
            'hp0': 11438,
            'atk0': 323,
            'df0': 953,
            'cr': 24.2,
            'cd': 50,
            'rcg': 100,
            'em': 0,
            'geo': 20, # chiori talent2
        }
        self.attrs = self.construct_attrs(chiori_base)
        self.mult = {
            'hasode-a': 269, # e release
            'hasode-d': 336, 
            'sode-a': 148, # e summon
            'sode-d': 185, 
            'hiyoku-a': 461, # q release
            'hiyoku-d': 576, 
            'a1-a': 97.7, # normal attack 1
            'c6-d': 235, # chiori c6
        }
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['goldentroupe', 'husk'],
        }
        self.recharge_thres = 150 # under which only cast q every 2 rotations
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()
       
    def apply_weapon(self):
        if self.weapon == 'misugiri':
            self.apply_misugiri()
        elif self.weapon == 'jade':
            self.apply_primodial_jade()

    def apply_misugiri(self, geo=True):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cd', 88.2)
        self.apply_modifier('normal', 16)
        self.apply_modifier('skill', 24)
        self.apply_modifier('D', 20)
        if geo:
            self.apply_modifier('skill', 24)

    def apply_primodial_jade(self):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cr', 44.1)
        self.apply_modifier('H', 20)

    def jade_atk(self):
        return (0.012 * self.hp())

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('goldentroupe', 2):
            self.apply_modifier('skill', 25)
        if self.artifacts.contains('goldentroupe', 4):
            self.apply_modifier('skill', 50)
        if self.artifacts.contains('husk', 2):
            self.apply_modifier('D', 30)
        if self.artifacts.contains('husk', 4):
            self.apply_modifier('D', 24)
            self.apply_modifier('geo', 24)

    def apply_resonation(self):
        self.apply_modifier('bns', 15) # geo resonation
        self.apply_modifier('res', -20)
    
    def reset_team(self):
        super().reset_stats()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)

    def apply_team(self, team=[]):
        if 'albedo' in team or 'gorou' in team or 'noelle' in team or 'zhongli' in team or 'navia' in team:
            self.apply_resonation()
        if 'gorou' in team:
            self.apply_modifier('d', 438) # skill
            self.apply_modifier('geo', 15) # skill
            self.apply_modifier('D', 25) # talent
            self.apply_modifier('cd', 40) # c6
        if 'furina' in team:
            self.apply_modifier('bns', 100) # fanfare
        if 'zhongli' in team:
            self.apply_modifier('geo', -20) # skill


    def optim_target(self, team=['furina', 'albedo', 'noelle'], args=['recharge_thres']):
        # returns hasode + sode*5*2 + tapestry*2 + hiyoku(*0.5)

        hiyoku_freq = 1
        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            hiyoku_freq = 0.5
        
        self.apply_team(team)
        
        # hasode (e) & tapestry (talent1)
        hasode_a = calc_damage(
            self.mult['hasode-a'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )
        
        hasode_d = calc_damage(
            self.mult['hasode-d'],
            self.df(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )
        
        # sode (e summon)
        sode_a = calc_damage(
            self.mult['sode-a'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )
        
        sode_d = calc_damage(
            self.mult['sode-d'],
            self.df(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )
        
        # hiyoku (q)
        hiyoku_a = calc_damage(
            self.mult['hiyoku-a'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','burst']),
            self.res()
        )
        
        hiyoku_d = calc_damage(
            self.mult['hiyoku-d'],
            self.df(), self.cr(), self.cd(), self.bns(['geo','burst']),
            self.res()
        )
        
        hasode = hasode_a + hasode_d
        sode = sode_a + sode_d
        hiyoku = hiyoku_a + hiyoku_d
        
        feature = hasode*3 + sode*10 + hiyoku*hiyoku_freq
        
        self.reset_team()

        return feature, {
            'hasode/tapestry': hasode,
            'sode': sode,
            'hiyoku': hiyoku,
            }
    

    def additional_feature(self, team=['furina', 'albedo', 'noelle'], args=['recharge_thres']):
        # returns c6 a1 damage

        self.apply_team(team)

        a1_a = calc_damage(
            self.mult['a1-a'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','normal']),
            self.res()
        )

        a1_c6 = calc_damage(
            self.mult['c6-d'],
            self.df(), self.cr(), self.cd(), self.bns(['geo','normal']),
            self.res()
        )

        a1 = a1_a + a1_c6

        return {
            'a1(pursuit)': a1,
            'pursuit': a1_c6,
            }
