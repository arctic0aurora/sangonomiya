from archive import *
from formation import *
from artifact import *

import numpy as np

class CharacterBase():
    def __init__(self):
        self.attrs = self.construct_attrs()
        self.artifacts = ArtifactCollection([])
    
    # get attributes
    def hp(self):
        return np.sum(self.attrs['hp0']) * (1 + 0.01*np.sum(self.attrs['H'])) + np.sum(self.attrs['h'])
    
    def atk(self):
        return np.sum(self.attrs['atk0']) * (1 + 0.01*np.sum(self.attrs['A'])) + np.sum(self.attrs['a'])
    
    def df(self):
        return np.sum(self.attrs['df0']) * (1 + 0.01*np.sum(self.attrs['D'])) + np.sum(self.attrs['d'])
    
    def spd(self):
        return np.sum(self.attrs['spd0']) * (1 + 0.01*np.sum(self.attrs['S'])) + np.sum(self.attrs['s'])
    
    def cr(self):
        return np.sum(self.attrs['cr'])
    
    def cd(self):
        return np.sum(self.attrs['cd'])
    
    def rcg(self):
        return np.sum(self.attrs['rcg'])
    
    def bns(self, tags=[]):
        bonus = np.sum(self.attrs['bns'])
        for tag in tags:
            bonus += np.sum(self.attrs[tag])
        return bonus
    
    def em(self):
        return np.sum(self.attrs['em'])
    
    def res(self):
        return np.sum(self.attrs['res'])
    
    def rdf(self):
        return np.sum(self.attrs['rdf'])
    
    # construct self.attrs from a simplified dict
    def construct_attrs(self, params={}):
        attrs = {
            'hp0': np.array([15000]), # hitpoint
            'atk0': np.array([1000]), # attack
            'df0': np.array([750]), # defence
            'spd0': np.array([100]), # speed
            'cr': np.array([5]), # crit rate
            'cd': np.array([50]), # crit damage
            'rcg': np.array([100]), # recharge
            'bns': np.array([0]), # damage bonus
            'em': np.array([0]), # elemental mastery
            'res': np.array([10]), # resistance (reduction)
            'rdf': np.array([0]), # defence reduction
            'H': np.array([0]), # hp percentage
            'h': np.array([0]), # hp increment
            'A': np.array([0]), # atk percentage
            'a': np.array([0]), # atk increment
            'D': np.array([0]), # def percentage
            'd': np.array([0]), # def increment
            'S': np.array([0]), # spd percentage
            's': np.array([0]), # spd increment
            # damage bonus tags (no getattribute) 
            'anemo': np.array([0]), # anemo dmg bonus
            'cryo': np.array([0]), # cryo dmg bonus
            'hydro': np.array([0]), # hydro dmg bonus
            'pyro': np.array([0]), # pyro dmg bonus
            'electro': np.array([0]), # electro dmg bonus
            'geo': np.array([0]), # geo dmg bonus
            'dendro': np.array([0]), # dendro dmg bonus
            'normal': np.array([0]), # normal atk dmg bonus
            'charged': np.array([0]), # charged atk dmg bonus
            'plunge': np.array([0]), # plunge atk dmg bonus
            'skill': np.array([0]), # skill dmg bonus
            'burst': np.array([0]), # burst dmg bonus
        }
        for key in params:
            attrs[key] = np.array([params[key]])
        # self.attrs = attrs
        return attrs
    
    # np.append wrapper
    def apply_modifier(self, stat, value):
        self.attrs[stat] = np.append(self.attrs[stat], value)
    
    # artifact management
    def apply_artifacts(self, artifacts):
        self.artifacts = artifacts
        artifact_attrs = self.artifacts.calculate_attrs()
        for key in artifact_attrs:
            if key in self.attrs and artifact_attrs[key] != 0:
                self.attrs[key] = np.append(self.attrs[key], artifact_attrs[key])
    
    def reset_stats(self):
        for key, value in self.attrs.items():
            if isinstance(value, np.ndarray):
                self.attrs[key] = np.array([value[0]])

    def get_panel(self):
        panel_stats = {
            'hp': self.hp(),
            'atk': self.atk(),
            'df': self.df(),
            'spd': self.spd(),
            'cr': self.cr(),
            'cd': self.cd(),
            'rcg': self.rcg(),
            'bns': self.bns(),
            'em': self.em()
        }
        return CharacterPanel(self.name, panel_stats)
    
    # calculations
    def optim_target(self):
        return Composite(), {}
    
    # misc helper functions
    def apply_a18_artifacts(self):
        for artifact_set in ['gladiator', 'reminiscence', 'echoes', 'vermillion', 'nighttime']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('A', 18)

    def apply_h20_artifacts(self):
        for artifact_set in ['millelith', 'vourukasha']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('H', 20)

    def apply_e80_artifacts(self):
        for artifact_set in ['troupe', 'gilded', 'paradise']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('em', 80)


class CharacterPanel():
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats
    
    def print(self, mask=all_mask):
        print(self.name)
        for key, value in self.stats.items():
            if key in mask and key in attribute_names:
                print('{}: {:.1f}'.format(attribute_names[key], value))


if __name__ == '__main__':
    kokomi = CharacterBase()
    kokomi_stats = kokomi.get_panel()
    kokomi_stats.print()


    
    
    

