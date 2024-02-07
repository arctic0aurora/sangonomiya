from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Chiori(CharacterBase):
    def __init__(self, weapon='yuraku'):
        super().__init__()
        self.name = 'Chiori'
        self.attrs = {
            'hp0': np.array([11437]), # hitpoint
            'atk0': np.array([323]), # attack
            'df0': np.array([953]), # defence
            'spd0': np.array([100]), # speed
            'cr': np.array([24.2]), # crit rate
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
            'geo': np.array([20]), # geo damage bonus [chiori talent2]
            'skill': np.array([0]), # skill damage bonus
        }
        self.prune_cond = {
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
        elif self.weapon == 'jade':
            self.apply_primodial_jade()

    def apply_primodial_jade(self):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 542)
        self.attrs['cr'] = np.append(self.attrs['cr'], 44.1)
        self.attrs['H'] = np.append(self.attrs['H'], 20)

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
        
    
    def optim_target(self, team=['furina', 'albedo', 'noelle'], args=['recharge_thres']):
        if 'recharge_thres' in args and self.rcg() < 100:
            return Composite(), {}

        skill_amult = 268.70
        skill_dmult = 335.88
        summon_amult = 147.74
        summon_dmult = 184.68
        burst_amult = 651.45
        burst_dmult = 814.32

        self.apply_team(team)

        skill_a = calc_damage(skill_amult,
            self.atk(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
            self.res(), self.rdf())
        
        skill_d = calc_damage(skill_dmult,
            self.df(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
            self.res(), self.rdf())
        
        summon_a = calc_damage(summon_amult,
            self.atk(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
            self.res(), self.rdf())
        
        summon_d = calc_damage(summon_dmult,
            self.df(), self.cr(), self.cd(), self.bns()+self.geo()+self.skill(),
            self.res(), self.rdf())
        
        burst_a = calc_damage(burst_amult,
            self.atk(), self.cr(), self.cd(), self.bns()+self.geo(),
            self.res(), self.rdf())
        
        burst_d = calc_damage(burst_dmult,
            self.df(), self.cr(), self.cd(), self.bns()+self.geo(),
            self.res(), self.rdf())
        
        skill = skill_a + skill_d
        summon = summon_a + summon_d
        burst = burst_a + burst_d

        feature = skill*(1+2) + summon*(5*2) + burst
        
        self.reset_team()

        return feature, {'summon': summon,
                         'skill': skill, 
                         'burst': burst, 
                         'summon(atk)': summon_a,
                         'summon(def)': summon_d,}