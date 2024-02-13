from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np


class Neuvillette(CharacterBase):
    def __init__(self, weapon='eternalflow'):
        self.name = 'Neuvillette'
        self.weapon = weapon
        neuvillette_base = {
            'hp0': 14695,
            'atk0': 208,
            'df0': 576,
            'cr': 5,
            'cd': 88.4,
            'rcg': 100,
            'em': 0,
            'hydro': 30 # talent2
        }
        self.attrs = self.construct_attrs(neuvillette_base)
        self.mult = {
            'judgment': 14.47, # charged: equitable judgment (8 per release C0)
            'tear-repay': 23.16, # e release
            'tide-return': 40.06, # q release
            'tide-return-waterfall': 16.39, # q following
        }
        self.authority = 1.6 # 3 stacks
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['marechaussee'],
        }
        self.recharge_thres = 115
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()
    
    def apply_weapon(self):
        if self.weapon == 'eternalflow':
            self.apply_eternalflow()
        elif self.weapon == 'windprayer':
            self.apply_windprayer()
        elif self.weapon == 'jade':
            self.apply_sacrificial_jade()
        elif self.weapon == 'prototype':
            self.apply_prototype_amber()
    
    # tome of the eternal flow
    def apply_eternalflow(self):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cd', 88.2)
        self.apply_modifier('H', 16)
        self.apply_modifier('charged', 42)

    # lost prayer to the sacred winds
    def apply_windprayer(self):
        # suppose max stack
        self.apply_modifier('atk0', 608)
        self.apply_modifier('cr', 33.1)
        self.apply_modifier('bns', 32)

    def apply_sacrificial_jade(self):
        # refinement 5
        self.apply_modifier('atk0', 454)
        self.apply_modifier('cr', 36.8)
        self.apply_modifier('H', 64)
        self.apply_modifier('em', 80)

    def apply_prototype_amber(self):
        self.apply_modifier('atk0', 510)
        self.apply_modifier('H', 41.3)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('marechaussee', 2):
            self.apply_modifier('normal', 15)
            self.apply_modifier('charged', 15)
        if self.artifacts.contains('marechaussee', 4):
            self.apply_modifier('cr', 36)
        if self.artifacts.contains('depth', 4):
            self.apply_modifier('normal', 30)
            self.apply_modifier('charged', 30)
        self.apply_h20_artifacts()
        for artifact_set in ['depth', 'nymph']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('hydro', 15)

    def apply_hydro_resonation(self):
        self.apply_modifier('H', 25)
    
    def reset_team(self):
        super().reset_stats()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)

    def apply_team(self, team=[]):
        if 'furina' in team:
            self.apply_hydro_resonation()
        if 'kazuha' in team:
            self.apply_modifier('A', 20) # freedom-sworn
            self.apply_modifier('normal', 16) # freedom-sworn
            self.apply_modifier('charged', 16) # freedom-sworn
            self.apply_modifier('plunge', 16) # freedom-sworn            
            self.apply_modifier('res', -40) # viridescent4
            self.apply_modifier('hydro', 42) # talent
        if 'furina' in team:
            self.apply_modifier('bns', 100) # fanfare


    def optim_target(self, team=['kazuha', 'furina', 'baizhu'], args=['recharge_thres']):
        # returns charged attack damage

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}
        
        self.apply_team(team)
        
        # mademoiselle crabaletta
        large_initial = calc_damage(
            self.mult['large'],
            self.hp(), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.res()
        )
        
        large_rejoice = calc_damage(
            self.mult['large'],
            self.hp(), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(400)+self.confession_bonus(400),
            self.res()
        )
        
        large_duckweed = calc_damage(
            self.mult['large'],
            self.hp()+self.fanfare_hp(800), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(800)+self.confession_bonus(800),
            self.res()
        )
        
        feature = large_duckweed*self.duckweed_weight + large_rejoice*(self.rejoice_weight-self.duckweed_weight) + large_initial*(1-self.rejoice_weight)
        
        self.reset_team()

        return feature, {}
    

    def additional_feature(self, team=['kazuha', 'kokomi', 'yelan'], args=['recharge_thres']):
        # returns rotation damage q+e 18s

        self.apply_team(team)

        # elemental burst
        rejoice = calc_damage(
            self.mult['rejoice'],
            self.hp(), self.cr(), self.cd(), self.bns(['hydro','burst'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.res()
        )
        
        # elemental skill release
        bubble = calc_damage(
            self.mult['solitaire-bubble'],
            self.hp(), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.res()
        )
        
        # calculate 3 summons with unit damage
        unit_initial = calc_damage(
            1,
            self.hp(), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.res()
        )
        
        unit_rejoice = calc_damage(
            1,
            self.hp(), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(400)+self.confession_bonus(400),
            self.res()
        )
        
        unit_duckweed = calc_damage(
            1,
            self.hp()+self.fanfare_hp(800), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(800)+self.confession_bonus(800),
            self.res()
        )

        salon_cumulative = Composite()
        for action in Furina.fanfare_sequence:
            action_result = calc_damage(
                self.mult[action['type']],
                self.hp()+self.fanfare_hp(action['fanfare']), self.cr(), self.cd(), self.bns(['hydro','skill'])+self.fanfare_bonus(action['fanfare'])+self.confession_bonus(action['fanfare']),
                self.res()
            )
            salon_cumulative = salon_cumulative + action_result
        
        self.reset_team()

        return {
            'rotation total': rejoice+bubble+salon_cumulative,
            'salon solitaire total': salon_cumulative,
            'rejoice': rejoice,
            'ousia bubble': bubble,
            'surintendante chevalmarin(initial)': unit_initial*self.mult['small'],
            'surintendante chevalmarin(rejoice)': unit_rejoice*self.mult['small'],
            'surintendante chevalmarin(duckweed)': unit_duckweed*self.mult['small'],
            'gentilhomme usher(initial)': unit_initial*self.mult['medium'],
            'gentilhomme usher(rejoice)': unit_rejoice*self.mult['medium'],
            'gentilhomme usher(duckweed)': unit_duckweed*self.mult['medium'],
            'mademoiselle crabaletta(initial)': unit_initial*self.mult['large'],
            'mademoiselle crabaletta(rejoice)': unit_rejoice*self.mult['large'],
            'mademoiselle crabaletta(duckweed)': unit_duckweed*self.mult['large'],
            }







