from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Furina(CharacterBase):
    def __init__(self, weapon='jade', fanfare_weight=0.5, duckweed_weight=0.33):
        self.name = 'Furina'
        self.weapon = weapon
        self.qweight = fanfare_weight
        self.c2weight = duckweed_weight
        furina_base = {
            'hp0': 15307,
            'atk0': 244,
            'df0': 696,
            'cr': 24.2,
            'cd': 50,
            'rcg': 100,
            'em': 0,
        }
        self.attrs = self.construct_attrs(furina_base)
        self.prune_cond = {
            'thres': 0,
            'set_restriction': {'goldentroupe': 4}
        }
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()

    # furina talent2
    def confession_bns(self, duckweed_hp=0):
        return min(28, (self.hp()+duckweed_hp)*0.7/1000)
    
    def apply_weapon(self):
        if self.weapon == 'tranquil':
            self.apply_tranquil()
        elif self.weapon == 'misugiri':
            self.apply_misugiri()
        elif self.weapon == 'jade':
            self.apply_primodial_jade()
    
    def apply_tranquil(self):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cd', 88.2)
        self.apply_modifier('H', 28)
        self.apply_modifier('skill', 24)

    def apply_misugiri(self, geo=False):
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

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('goldentroupe', 2):
            self.apply_modifier('skill', 25)
        if self.artifacts.contains('goldentroupe', 4):
            self.apply_modifier('skill', 50)
        if self.artifacts.contains('emblem', 2):
            self.apply_modifier('rcg', 20)
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
        if 'kokomi' in team or 'yelan' in team or 'xingqiu' in team:
            self.apply_hydro_resonation()
        if 'kazuha' in team:
            self.apply_modifier('A', 20) # freedom-sworn            
            self.apply_modifier('res', -40) # viridescent4
            self.apply_modifier('cryo', 42) # talent
        if 'lynette' in team or 'jean' in team:          
            self.apply_modifier('res', -40) # viridescent4
        if 'yelan' in team:
            # self.apply_modifier('bns', 28) # talent
            self.apply_modifier('bns', 0) # no buff for off-field
        if 'xingqiu' in team:
            self.apply_modifier('res', -15) # c2


    def optim_target(self, team=['kazuha', 'kokomi', 'yelan'], args=['recharge_thres']):
        # rotation e summon damage as feature

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