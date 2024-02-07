from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Furina(CharacterBase):
    def __init__(self, weapon='jade', fanfare_weight=0.5, duckweed_weight=0.33):
        super().__init__()
        self.name = 'Furina'
        self.attrs = {
            'hp0': np.array([15307]), # hitpoint
            'atk0': np.array([244]), # attack
            'df0': np.array([696]), # defence
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
        }
        self.prune_cond = {
            'thres': 0,
            'set_restriction': {'goldentroupe':4}
        }
        self.qweight = fanfare_weight
        self.c2weight = duckweed_weight
        self.weapon = weapon      
        self.apply_weapon()
        self.apply_resonation()
        # self.apply_team()
    
    def apply_weapon(self):
        if self.weapon == 'yuraku':
            self.apply_yuraku()
        elif self.weapon == 'jade':
            self.apply_primodial_jade()

    def confession_bns(self, duckweed_hp=0):
        return min(28, (self.hp()+duckweed_hp)*0.7/1000)

    def apply_primodial_jade(self):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 542)
        self.attrs['cr'] = np.append(self.attrs['cr'], 44.1)
        self.attrs['H'] = np.append(self.attrs['H'], 20)

    def apply_yuraku(self):
        self.attrs['atk0'] = np.append(self.attrs['atk0'], 542)
        self.attrs['cd'] = np.append(self.attrs['cd'], 88.2)
        self.attrs['bns'] = np.append(self.attrs['bns'], 24)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if 'goldentroupe' in self.artifacts.set_counts and self.artifacts.set_counts['goldentroupe'] >= 2:
            self.attrs['bns'] = np.append(self.attrs['bns'], 25)
        if 'goldentroupe' in self.artifacts.set_counts and self.artifacts.set_counts['goldentroupe'] >= 4:
            self.attrs['bns'] = np.append(self.attrs['bns'], 50)
        if 'depth' in self.artifacts.set_counts and self.artifacts.set_counts['depth'] >= 2:
            self.attrs['bns'] = np.append(self.attrs['bns'], 15)
        if 'millelith' in self.artifacts.set_counts and self.artifacts.set_counts['millelith'] >= 2:
            self.attrs['H'] = np.append(self.attrs['H'], 20)
        if 'vourukasha' in self.artifacts.set_counts and self.artifacts.set_counts['vourukasha'] >= 2:
            self.attrs['H'] = np.append(self.attrs['H'], 20)
        if 'echoes' in self.artifacts.set_counts and self.artifacts.set_counts['echoes'] >= 2:
            self.attrs['A'] = np.append(self.attrs['A'], 18)
        if 'troupe' in self.artifacts.set_counts and self.artifacts.set_counts['troupe'] >= 2:
            self.attrs['em'] = np.append(self.attrs['em'], 80)
        if 'emblem' in self.artifacts.set_counts and self.artifacts.set_counts['emblem'] >= 2:
            self.attrs['rcg'] = np.append(self.attrs['rcg'], 20)

    def apply_resonation(self):
        self.attrs['H'] = np.append(self.attrs['H'], 25) # hydro resonation
    
    def reset_team(self):
        super().reset_stats()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)
        self.apply_resonation()

    def apply_team(self, team=[]):
        if 'kazuha' in team:
            self.attrs['A'] = np.append(self.attrs['A'], 20) # freedom-sworn            
            self.attrs['res'] = np.append(self.attrs['res'], -40) # viridescent4
            self.attrs['bns'] = np.append(self.attrs['bns'], 42) # talent
        if 'jean' in team:
            self.attrs['A'] = np.append(self.attrs['A'], 20) # freedom-sworn 
            self.attrs['res'] = np.append(self.attrs['res'], -40) # viridescent4
        if 'yelan' in team:
            self.attrs['bns'] = np.append(self.attrs['bns'], 28) # talent
        if 'xingqiu' in team:
            self.attrs['res'] = np.append(self.attrs['res'], -15) # talent
    
    def optim_target(self, team=['kazuha', 'kokomi', 'xingqiu'], args=['recharge_thres']):
        if 'recharge_thres' in args and self.rcg() < 155:
            return Composite(), {}

        ousia_bubble = 14.2
        gentilhomme_usher = 10.73
        surintendante_chevalmarin = 5.82
        mademoiselle_crabaletta = 14.92

        fanfare_bns = 400 * 0.25
        duckweed_hp = 1.40

        self.apply_team(team)

        # bubble has no fanfare bonus
        bubble = calc_damage(ousia_bubble,
            self.hp(), self.cr(), self.cd(), self.bns(),
            self.res())
        
        # without fanfare
        small_initial = calc_damage(surintendante_chevalmarin,
            self.hp(), self.cr(), self.cd(), self.bns()+self.confession_bns(),
            self.res())
        medium_initial = calc_damage(gentilhomme_usher,
            self.hp(), self.cr(), self.cd(), self.bns()+self.confession_bns(),
            self.res())
        large_initial = calc_damage(mademoiselle_crabaletta,
            self.hp(), self.cr(), self.cd(), self.bns()+self.confession_bns(),
            self.res())
        
        # full fanfare
        small_full = calc_damage(surintendante_chevalmarin,
            self.hp(), self.cr(), self.cd(), self.bns()+fanfare_bns+self.confession_bns(),
            self.res())
        medium_full = calc_damage(gentilhomme_usher,
            self.hp(), self.cr(), self.cd(), self.bns()+fanfare_bns+self.confession_bns(),
            self.res())
        large_full = calc_damage(mademoiselle_crabaletta,
            self.hp(), self.cr(), self.cd(), self.bns()+fanfare_bns+self.confession_bns(),
            self.res())
        
        # with duckweed bonus
        small_c2full = calc_damage(surintendante_chevalmarin,
            self.hp()+duckweed_hp*self.attrs['hp0'][0], self.cr(), self.cd(), self.bns()+fanfare_bns+self.confession_bns(duckweed_hp*self.attrs['hp0'][0]),
            self.res())
        medium_c2full = calc_damage(gentilhomme_usher,
            self.hp()+duckweed_hp*self.attrs['hp0'][0], self.cr(), self.cd(), self.bns()+fanfare_bns+self.confession_bns(duckweed_hp*self.attrs['hp0'][0]),
            self.res())
        large_c2full = calc_damage(mademoiselle_crabaletta,
            self.hp()+duckweed_hp*self.attrs['hp0'][0], self.cr(), self.cd(), self.bns()+fanfare_bns+self.confession_bns(duckweed_hp*self.attrs['hp0'][0]),
            self.res())
        
        feature = (small_initial*(1-self.qweight-self.c2weight) + small_full*self.qweight + small_c2full*self.c2weight)*12
        feature = feature + (medium_initial*(1-self.qweight-self.c2weight) + medium_full*self.qweight + medium_c2full*self.c2weight)*6
        feature = feature + (large_initial*(1-self.qweight-self.c2weight) + large_full*self.qweight + large_c2full*self.c2weight)*6

        self.reset_team()

        return feature, {'ousia bubble': bubble,
                         'surintendante_chevalmarin(fanfare)': small_full, 
                         'gentilhomme_usher(fanfare)': medium_full, 
                         'mademoiselle_crabaletta(fanfare)': large_full,
                         'surintendante_chevalmarin(duckweed)': small_c2full, 
                         'gentilhomme_usher(duckweed)': medium_c2full, 
                         'mademoiselle_crabaletta(duckweed)': large_c2full}