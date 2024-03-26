from archive import *
from formation import *
from artifact import *
from attributes import *

import numpy as np


class CharacterPanel():
    def __init__(self, name, attrs=CharacterAttrs()):
        self.name = name
        self.attrs = attrs
    
    def print(self, level=0, params=SangonomiyaArchive.genshin_panel):
        print(self.name)
        if level == 0:
            self.attrs.print(params)
        elif level > 0:
            self.attrs.print_all(params)


class CharacterBase():
    def __init__(self, name='character'):
        self.name = name
        self.attrs = CharacterAttrs()
        self.artifacts = ArtifactCollection([])
        self.construct_attrs()
    
    # construct self.attrs from a simplified dict
    def construct_attrs(self, params={}):
        simple_attrs = {
            'hp0': 15000, # hitpoint
            'atk0': 1000, # attack
            'df0': 700, # defence
            'spd0': 100, # speed (in hsr)
            'cr': 5, # crit rate
            'cd': 50, # crit damage
            'rcg': 100, # recharge
            'bns': 0, # damage bonus
            'em': 0, # elemental mastery
            'res': 10, # resistance (reduction)
            'rdf': 0, # defence reduction
            'H': 0, # hp percentage
            'h': 0, # hp increment
            'A': 0, # atk percentage
            'a': 0, # atk increment
            'D': 0, # def percentage
            'd': 0, # def increment
            'S': 0, # spd percentage
            's': 0, # spd increment
            # damage bonus tags
            'anemo': 0, # anemo dmg bonus
            'cryo': 0, # cryo dmg bonus
            'hydro': 0, # hydro dmg bonus
            'pyro': 0, # pyro dmg bonus
            'electro': 0, # electro dmg bonus
            'geo': 0, # geo dmg bonus
            'dendro': 0, # dendro dmg bonus
            'physical': 0, # physical dmg bonus
            'normal': 0, # normal atk dmg bonus
            'charged': 0, # charged atk dmg bonus
            'plunge': 0, # plunge atk dmg bonus
            'skill': 0, # skill dmg bonus
            'burst': 0, # burst dmg bonus
        }
        for key in params:
            simple_attrs[key] = params[key]
        self.attrs.construct_list(simple_attrs)
    
    # get wrapper
    def get(self, attr, secondary_attrs=[], t=-1):
        return self.attrs.get_attr_wrapper(attr, secondary_attrs, t)
    
    # append wrapper
    def apply_modifier(self, attr, value, t0=0, t1=65535, name=''):
        self.attrs.append_modifier(attr, value, t0, t1, name)
    
    # artifact management
    def apply_artifacts(self, artifacts):
        self.artifacts = artifacts
        artifact_attrs = self.artifacts.calculate_attrs()
        for key in artifact_attrs:
            if artifact_attrs[key] != 0:
                self.attrs.append_modifier(key, artifact_attrs[key], name='artifacts')
    
    # reset wrapper
    def reset_attrs(self):
        self.attrs.reset_list()

    # get character panel
    def snapshot(self):
        return CharacterPanel(self.name, self.attrs)
    
    # team
    def apply_team(self, team):
        pass

    def reset_team(self):
        pass
    
    # calculations
    def optim_target(self, team, args):
        return Composite(), {}
    
    def additional_feature(self, team, args):
        return {}
    
    # misc helper functions
    def in_team(self, chara, team):
        for c in team:
            if chara in c: # for example, furina is true if furina-favonius in team
                return True
        return False

    def apply_a18_artifacts(self):
        for artifact_set in ['gladiator', 'reminiscence', 'echoes', 'vermillion', 'nighttime']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('A', 18, name='a18-set2')

    def apply_h20_artifacts(self):
        for artifact_set in ['millelith', 'vourukasha']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('H', 20, name='h20-set2')

    def apply_e80_artifacts(self):
        for artifact_set in ['troupe', 'gilded', 'paradise']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('em', 80, name='em80-set2')


if __name__ == '__main__':
    # praise kokomi~
    kokomi = CharacterBase(name='Sangonomiya Kokomi')
    kokomi_stats = kokomi.snapshot()
    kokomi_stats.print(0)


    
    
    

