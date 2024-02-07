from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Noelle(CharacterBase):
    def __init__(self, weapon='skyward'):
        super().__init__()
        self.name = 'Noelle'
        self.attrs = {
            'hp0': np.array([12071]), # hitpoint
            'atk0': np.array([191]), # attack
            'df0': np.array([799]), # defence
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
            'D': np.array([30]), # def percentage
            'd': np.array([0]), # def increment
            'S': np.array([0]), # spd percentage
            's': np.array([0]), # spd increment
            'geo': np.array([0]), # geo damage bonus
            'norm': np.array([0]), # normal/charged damage bonus
        }
        self.prune_cond = {
            'thres': 0,
            'set_restriction': {'marechaussee':4},
            'alternative': {'husk':4}
        }
        self.weapon = weapon   
        self.apply_weapon()
        self.apply_resonation()
        # self.apply_team()

    def geo(self):
        return np.sum(self.attrs['geo'])
    
    def norm(self):
        return np.sum(self.attrs['norm'])
    
    
    def apply_weapon(self):
        if self.weapon == 'skyward':
            self.apply_skyward()
        elif self.weapon == 'serpent':
            self.apply_serpent()
        elif self.weapon == 'redhorn':
            self.apply_redhorn()

    def apply_skyward(self, refinement=4):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 674)
        self.attrs['rcg'] = np.append(self.attrs['rcg'], 36.8)
        self.attrs['bns'] = np.append(self.attrs['bns'], 14)

    def apply_serpent(self, refinement=5):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 510)
        self.attrs['cr'] = np.append(self.attrs['cr'], 27.6)
        self.attrs['bns'] = np.append(self.attrs['bns'], 50)

    def apply_redhorn(self):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 542)
        self.attrs['cd'] = np.append(self.attrs['cd'], 88.2)
        self.attrs['D'] = np.append(self.attrs['D'], 28)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if 'marechaussee' in self.artifacts.set_counts and self.artifacts.set_counts['marechaussee'] >= 2:
            self.attrs['norm'] = np.append(self.attrs['norm'], 15) # normal/charged bonus
        if 'marechaussee' in self.artifacts.set_counts and self.artifacts.set_counts['marechaussee'] >= 4:
            self.attrs['cr'] = np.append(self.attrs['cr'], 36)
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
        if 'yelan' in team:
            self.attrs['bns'] = np.append(self.attrs['bns'], 28) # talent
    
    def optim_target(self, team=['furina', 'albedo', 'chiori'], args=['recharge_thres']):
        if 'recharge_thres' in args and self.rcg() < 130:
            return Composite(), {}

        normal_mult = 156 + 145 + 171 + 224
        breastplate_mult = 255
        breastplate_broken_mult = 400
        sweeping_mult = 143 + 197

        conversion = 0.85 + 0.5

        self.apply_team(team)

        normal = calc_damage(normal_mult,
            self.atk()+conversion*self.df(), self.cr(), self.cd(), self.bns()+self.norm()+self.geo(),
            self.res(), self.rdf())
        
        breastplate = calc_damage(breastplate_mult+breastplate_broken_mult,
            self.df(), self.cr(), self.cd(), self.bns()+self.geo(),
            self.res(), self.rdf())
        
        sweeping = calc_damage(sweeping_mult,
            self.atk()+conversion*self.df(), self.cr(), self.cd(), self.bns()+self.geo(),
            self.res(), self.rdf())
        
        skyward, redhorn = Composite(), Composite()

        if self.weapon == 'skyward':
            skyward = calc_damage(140,
                self.atk()+conversion*self.df(), self.cr(), self.cd(), self.bns()+self.norm(),
                10, self.rdf())       
        elif self.weapon == 'redhorn':
            redhorn = calc_damage(40,
                self.df(), self.cr(), self.cd(), self.bns()+self.norm(),
                self.res(), self.rdf()) 
        
        feature = normal*4 + breastplate + sweeping + skyward*8 + redhorn*16

        self.reset_team()

        return feature, {'normal4': normal,
                         'breastplate': breastplate, 
                         'sweeping': sweeping, 
                         'skyward': skyward,}