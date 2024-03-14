from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Noelle(CharacterBase):   
    def __init__(self, weapon='redhorn'):
        self.name = 'Noelle'
        self.weapon = weapon
        noelle_base = {
            'hp0': 12071,
            'atk0': 191,
            'df0': 799,
            'cr': 5,
            'cd': 50,
            'rcg': 100,
            'D': 30,
        }
        self.attrs = self.construct_attrs(noelle_base)
        self.mult = {
            'a1': 156, # favonius bladework maid
            'a2': 145, 
            'a3': 171, 
            'a4': 224, 
            'breastplate-create': 255, # e release (def)
            'breastplate-expire': 400, # c4
            'sweeping-burst': 121, # q release
            'sweeping-strike': 167, # q sweep attack
        }
        self.conversion = 1.35 # 0.85(q13) + 0.5(c6)
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['marechaussee', 'husk'],
        }
        self.recharge_thres = 125 # do I really need so much recharge?
        self.redhorn_mult = 0
        self.skyward_mult = 0
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()
    
    def sweeping_atk(self):
        return self.atk() + self.conversion * self.df()
       
    def apply_weapon(self):
        if self.weapon == 'redhorn':
            self.apply_redhorn()
        elif self.weapon == 'skyward':
            self.apply_skyward()
        elif self.weapon == 'serpent':
            self.apply_serpent()

    def apply_redhorn(self):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cd', 88.2)
        self.apply_modifier('D', 28)
        self.redhorn_mult = 40
    
    def apply_skyward(self, refinement=4):
        self.apply_modifier('atk0', 674)
        self.apply_modifier('rcg', 36.8)
        self.apply_modifier('bns', 6+2*refinement)
        self.skyward_mult = 60+20*refinement

    def apply_serpent(self, refinement=5):
        self.apply_modifier('atk0', 510)
        self.apply_modifier('cr', 27.6)
        self.apply_modifier('bns', 50)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('marechaussee', 2):
            self.apply_modifier('normal', 15)
            self.apply_modifier('charged', 15)
        if self.artifacts.contains('marechaussee', 4):
            self.apply_modifier('cr', 36)
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
        if 'albedo' in team or 'gorou' in team or 'chiori' in team or 'zhongli' in team:
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
        if 'yelan' in team:
            self.apply_modifier('bns', 28) # talent
    
    
    def optim_target(self, team=['albedo', 'gorou', 'furina'], args=['recharge_thres']):
        # returns rotation damage

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}

        self.apply_team(team)

        normal_cumulative, maid_bladework = Composite(), Composite()
        for action in ['a4', 'a3', 'a2', 'a1']:
            maid_bladework = calc_damage(
                self.mult[action],
                self.sweeping_atk(), self.cr(), self.cd(), self.bns(['geo','normal']),
                self.res()
            )
            normal_cumulative = normal_cumulative + maid_bladework
        
        breastplate_create = calc_damage(
            self.mult['breastplate-create'],
            self.df(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )
        breastplate_expire = calc_damage(
            self.mult['breastplate-expire'],
            self.sweeping_atk(), self.cr(), self.cd(), self.bns(['geo','skill']),
            self.res()
        )

        sweeping_time = calc_damage(
            self.mult['sweeping-burst']+self.mult['sweeping-strike'],
            self.sweeping_atk(), self.cr(), self.cd(), self.bns(['geo','burst']),
            self.res()
        )
        
        skyward_vacuum_blade, redhorn_extra = Composite(), Composite()
        if self.weapon == 'redhorn':
            redhorn_extra = calc_damage(
                self.redhorn_mult,
                self.df(), self.cr(), self.cd(), self.bns(['geo','normal']),
                self.res()
            )
        elif self.weapon == 'skyward':
            skyward_vacuum_blade = calc_damage(
                self.skyward_mult,
                self.sweeping_atk(), self.cr(), self.cd(), self.bns(['physical','normal']),
                self.res()
            )
        
        normal_round = normal_cumulative + redhorn_extra*4
        normal1 = maid_bladework + redhorn_extra
        feature = normal_round*5 + breastplate_create + breastplate_expire + sweeping_time + skyward_vacuum_blade*8
        
        self.reset_team()

        return feature, {           
            'favonius blade maid round': normal_round,
            'favonius blade maid a1': normal1,
            'breastplate explode': breastplate_expire,
            'skyward vacuum blade': skyward_vacuum_blade,
            }
    
    def additional_feature(self, team=['albedo', 'gorou', 'furina'], args=['recharge_thres']):
        # returns none       
        return {}