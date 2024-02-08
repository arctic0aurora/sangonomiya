from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Albedo(CharacterBase):
    def __init__(self, weapon='spindle'):
        super().__init__()
        self.name = 'Albedo'
        self.attrs = {
            'hp0': np.array([13226]), # hitpoint
            'atk0': np.array([251]), # attack
            'df0': np.array([876]), # defence
            'spd0': np.array([100]), # speed
            'cr': np.array([5]), # crit rate
            'cd': np.array([50]), # crit damage
            'rcg': np.array([100]), # recharge
            'bns': np.array([0]), # damage bonus
            'em': np.array([0]), # elemental mastery
            'res': np.array([10]), # resistance (reduction)
            'rdf': np.array([0]), # defence (reduction)
            'H': np.array([0]), # hp percentage
            'h': np.array([0]), # hp increment
            'A': np.array([0]), # atk percentage
            'a': np.array([0]), # atk increment
            'D': np.array([0]), # def percentage
            'd': np.array([0]), # def increment
            'S': np.array([0]), # spd percentage
            's': np.array([0]), # spd increment
            'geo': np.array([28.8]), # geo damage bonus [chiori talent2]
            'skill': np.array([0]), # skill damage bonus
        }
        self.requirement = {
            'thres': 0,
            'set_restriction': {'goldentroupe':4},
            'alternative': {'husk':4}
        }
        self.weapon = weapon   
        self.apply_weapon()
        self.apply_resonation()
        # self.apply_team()

    def geo(self):
        return np.sum(self.attrs['geo'])
    
    def skill(self):
        return np.sum(self.attrs['skill'])
    
    
    def apply_weapon(self):
        if self.weapon == 'yuraku':
            self.apply_yuraku()
        elif self.weapon == 'spindle':
            self.apply_spindle()

    def apply_spindle(self):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 454)
        self.attrs['D'] = np.append(self.attrs['D'], 69.0)

    def apply_yuraku(self):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 542)
        self.attrs['cd'] = np.append(self.attrs['cd'], 88.2)
        self.attrs['skill'] = np.append(self.attrs['skill'], 48)
        self.attrs['D'] = np.append(self.attrs['D'], 20)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if 'goldentroupe' in self.artifacts.set_counts and self.artifacts.set_counts['goldentroupe'] >= 2:
            self.attrs['skill'] = np.append(self.attrs['skill'], 25)
        if 'goldentroupe' in self.artifacts.set_counts and self.artifacts.set_counts['goldentroupe'] >= 4:
            self.attrs['skill'] = np.append(self.attrs['skill'], 50)
        if 'husk' in self.artifacts.set_counts and self.artifacts.set_counts['husk'] >= 2:
            self.attrs['D'] = np.append(self.attrs['D'], 30)
        if 'husk' in self.artifacts.set_counts and self.artifacts.set_counts['husk'] >= 4:
            self.attrs['D'] = np.append(self.attrs['D'], 24)
            self.attrs['geo'] = np.append(self.attrs['geo'], 24)

    def apply_resonation(self):
        self.attrs['bns'] = np.append(self.attrs['bns'], 15) # geo resonation
        self.attrs['res'] = np.append(self.attrs['res'], -20)
    
    def reset_team(self):
        super().reset_stats()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)
        self.apply_resonation()

    def apply_team(self, team=[]):
        if 'gorou' in team:
            self.attrs['d'] = np.append(self.attrs['d'], 438) # skill
            self.attrs['geo'] = np.append(self.attrs['geo'], 15) # skill         
            self.attrs['D'] = np.append(self.attrs['D'], 25) # talent
            self.attrs['cd'] = np.append(self.attrs['cd'], 40) # c6
        if 'furina' in team:
            self.attrs['bns'] = np.append(self.attrs['bns'], 100) # fanfare
        if 'zhongli' in team:
            self.attrs['res'] = np.append(self.attrs['res'], -20) # skill
        
    
    def optim_target(self, team=['furina', 'chiori', 'noelle'], args=['recharge_thres']):
        if 'recharge_thres' in args and self.rcg() < 100:
            return Composite(), {}

        abiogenesis_mult = 235
        solar_isotoma_mult = 240
        progeniture_mult = 661
        blossom_mult = 129.6 # 7 blossoms
        spindle_mult = 80

        self.apply_team(team)

        abiogenesis = calc_damage(abiogenesis_mult,
            self.atk(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
            self.res(), self.rdf())
        
        solar_isotoma = calc_damage(solar_isotoma_mult,
            self.df(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
            self.res(), self.rdf())
        
        progeniture = calc_damage(progeniture_mult,
            self.atk(), self.cr(), self.cd(), self.bns()+self.geo(),
            self.res(), self.rdf())
        
        blossom = calc_damage(blossom_mult,
            self.atk(), self.cr(), self.cd(), self.bns()+self.geo(),
            self.res(), self.rdf())
        
        tecnotic_tide = progeniture + blossom*7

        spindle = Composite()    
        if self.weapon == 'spindle':
            spindle = calc_damage(spindle_mult,
                self.df(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
                self.res(), self.rdf())

        solar_isotoma = solar_isotoma + spindle
        feature = abiogenesis + solar_isotoma*10 + tecnotic_tide
        
        self.reset_team()

        return feature, {'solar isotoma': solar_isotoma,
                         'abiogenesis': abiogenesis, 
                         'progeniture': tecnotic_tide, }