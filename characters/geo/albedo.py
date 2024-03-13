from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Albedo(CharacterBase):
    def __init__(self, weapon='spindle'):
        self.name = 'Albedo'
        self.weapon = weapon
        albedo_base = {
            'hp0': 13226,
            'atk0': 251,
            'df0': 876,
            'cr': 5,
            'cd': 50,
            'rcg': 100,
            'geo': 28.8,
        }
        self.attrs = self.construct_attrs(albedo_base)
        self.mult = {
            'abiogenesis': 235, # e release (atk)
            'solar-isotoma': 240, # e summon (def) 
            'tectonic-tide': 661, # q release (atk)
            'fatal-blossom': 129.6, # q following (atk)
        }
        self.spindle_mult = 0
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['goldentroupe', 'husk'],
        }
        self.recharge_thres = 100
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()
       
    def apply_weapon(self):
        if self.weapon == 'misugiri':
            self.apply_misugiri()
        elif self.weapon == 'spindle':
            self.apply_spindle()

    def apply_misugiri(self, geo=True):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cd', 88.2)
        self.apply_modifier('normal', 16)
        self.apply_modifier('skill', 24)
        self.apply_modifier('D', 20)
        if geo:
            self.apply_modifier('skill', 24)

    def apply_spindle(self):
        self.apply_modifier('atk0', 454)
        self.apply_modifier('D', 69)
        self.spindle_mult = 80

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
        if 'chiori' in team or 'gorou' in team or 'noelle' in team or 'zhongli' in team or 'navia' in team:
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


    def optim_target(self, team=['noelle', 'gorou', 'furina'], args=['recharge_thres']):
        # returns rotation damage as feature

        progeniture_freq = 1
        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            progeniture_freq = 0.5 # q once per 2 rotations
        
        self.apply_team(team)
               
        solar_isotoma = calc_damage(
            self.mult['solar-isotoma'],
            self.df(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )
        spindle_extra = Composite()
        if self.weapon == 'spindle':
            spindle_extra = calc_damage(
                self.spindle_mult,
                self.df(), self.cr(), self.cd(), self.bns(['geo','skill']),
                self.res()
            )      
        solar_isotoma = solar_isotoma + spindle_extra

        abiogenesis = calc_damage(
            self.mult['abiogenesis'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )

        tectonic_tide = calc_damage(
            self.mult['tectonic-tide'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','burst']),
            self.res()
        )
        blossom = calc_damage(
            self.mult['fatal-blossom'],
            self.atk(), self.cr(), self.cd(), self.bns(['geo','burst']),
            self.res()
        )
        progeniture_rite = tectonic_tide + blossom*7

        feature = solar_isotoma*10 + abiogenesis + progeniture_rite * progeniture_freq
        
        self.reset_team()

        return feature, {
            'solar isotoma': solar_isotoma,
            'abiogenesis': abiogenesis,
            'progeniture rite': progeniture_rite,
            }
        
    def additional_feature(self, team=['noelle', 'gorou', 'furina'], args=['recharge_thres']):
        # returns none
        return {}
    