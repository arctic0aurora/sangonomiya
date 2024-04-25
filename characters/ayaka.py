from archive import *
from chara import *
from artifact import *
from attributes import *
from formation import *
from optim import *

import numpy as np

class Ayaka(CharacterBase):
    def __init__(self, weapon='mistsplitter', cryo_weight=1, frozen_weight=0.5):
        self.name = 'Ayaka'
        self.attrs = CharacterAttrs()
        self.artifacts = ArtifactCollection([])
        self.weapon = weapon
        self.cryo_weight = cryo_weight
        self.frozen_weight = frozen_weight
        self.cryo_cr = {
            'no': [],
            'cryo': ['cr-cryo'],
            'frozen': ['cr-cryo', 'cr-frozen'],
        }
        ayaka_base = {
            'hp0': 12858,
            'atk0': 342,
            'df0': 784,
            'cr': 5,
            'cd': 88.4,
            'rcg': 100,
            'em': 0,
            'cryo': 18, # ayaka talent2
            'rdf': -40, # ayaka c4
            'normal': 30, # ayaka talent1
            'charged': 30, # ayaka talent1
            'cr-cryo': 0, # additional crit rate when cryo
            'cr-frozen': 0, # additional crit rate when frozen
        }      
        self.construct_attrs(ayaka_base)
        self.mult = {
            'soumetsu-cut': 239,
            'soumetsu-bloom': 358,
            'hyouka': 508,
            'a1': 90.4,
            'charged': 109,
        } # skill lvl 10/13/13
        self.suigetsu_bonus = 298 # ayaka c6
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['blizzard'],
        }
        self.recharge_thres = 137 # tested with shenhe-favonius        
        self.apply_weapon()

    def apply_weapon(self):
        if self.weapon == 'mistsplitter':
            self.apply_mistsplitter()

    def apply_mistsplitter(self):
        self.apply_modifier('atk0', 674, name='mistsplitter')
        self.apply_modifier('cd', 44.1, name='mistsplitter')
        self.apply_modifier('bns', 12, name='mistsplitter')
        self.apply_modifier('cryo', 28, name='mistsplitter')

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('blizzard', 2):
            self.apply_modifier('cryo', 15, name='blizzard2')
        if self.artifacts.contains('blizzard', 4):
            self.apply_modifier('cr-cryo', 20, name='blizzard4')
            self.apply_modifier('cr-frozen', 20, name='blizzard4')
        if self.artifacts.contains('emblem', 2):
            self.apply_modifier('rcg', 20, name='emblem2')
        self.apply_a18_artifacts()

    def apply_cryo_resonation(self):
        self.apply_modifier('cr-cryo', 15, name='cryo-resonation')
    
    def reset_team(self):
        super().reset_attrs()
        self.apply_mistsplitter()
        self.apply_artifacts(self.artifacts)

    def apply_team(self, team):
        if self.in_team(team, ors=['shenhe', 'ganyu', 'layla']):
            self.apply_cryo_resonation()
        if self.in_team(team, ors=['kazuha', 'lynette', 'venti', 'sucrose']):
            self.apply_modifier('res', -40, name='viridescent4')
        if self.in_team(team, ors=['kazuha', 'lynette']):
            self.apply_modifier('A', 20, name='freedom-sworn')
            self.apply_modifier('normal', 16, name='freedom-sworn')
            self.apply_modifier('charged', 16, name='freedom-sworn')
            self.apply_modifier('plunge', 16, name='freedom-sworn')
        if self.in_team(team, 'kazuha'):
            self.apply_modifier('cryo', 42, name='kazuha-talent2')
        if self.in_team(team, 'lynette'):
            self.apply_modifier('A', 16, name='lynette-talent1')
        if self.in_team(team, 'venti'):
            self.apply_modifier('A', 20, name='elegy-for-the-end')
            self.apply_modifier('em', 100, name='elegy-for-the-end')
        if self.in_team(team, 'kokomi'):
            self.apply_modifier('A', 48, name='thrilling-tales')
            self.apply_modifier('A', 20, name='millelith4')
        if self.in_team(team, 'shenhe'):
            self.apply_modifier('A', 20, name='noblesse4')
            self.apply_modifier('res', -15, name='shenhe-burst')
            self.apply_modifier('cryo', 15, name='shenhe-talent1')
            self.apply_modifier('bns', 15, name='shenhe-talent2-merged')
        if self.in_team(team, 'shenhe-favonius'):
            self.apply_modifier('quill', 2513, name='shenhe-quill-favonius')
            # self.get('quill') = 2513 # favonius
        if self.in_team(team, 'ganyu'):
            self.apply_modifier('cryo', 20, name='ganyu-talent2')
        if self.in_team(team, 'zhongli'):
            self.apply_modifier('A', 20, name='millelith4')
            self.apply_modifier('res', -20, name='zhongli-skill')
    
    
    def optim_target(self, team=['kazuha', 'kokomi', 'shenhe-favonius'], args=['recharge_thres']):
        # returns full soumetsu with 10 quills as feature

        if 'recharge_thres' in args and self.get('rcg') < self.recharge_thres:
            return Composite(), {}

        self.apply_team(team)

        # soumetsu
        soumetsu_full = {}
        for cond in self.cryo_cr:
            soumetsu_full[cond] = calc_damage(
                1.4*(19*self.mult['soumetsu-cut']+self.mult['soumetsu-bloom']), # with c2 mini seki-no-tos
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','burst']),
                self.get('res'), self.get('rdf'),
                quill = 10*self.get('quill')
            )

        feature = soumetsu_full['frozen']*self.frozen_weight + soumetsu_full['cryo']*(self.cryo_weight-self.frozen_weight) + soumetsu_full['no']*(1-self.cryo_weight)

        self.reset_team()

        return feature, {
            'soumetsu full': soumetsu_full['frozen'], 
            }


    def additional_feature(self, team=['kazuha', 'kokomi', 'shenhe-favonius'], args=['recharge_thres']):
        # returns soumetsu and c6 charged damage

        if 'recharge_thres' in args and self.get('rcg') < self.recharge_thres:
            return Composite(), {}

        # alone without team buffs
        soumetsu_cut_alone = {}
        for cond in self.cryo_cr:
            soumetsu_cut_alone[cond] = calc_damage(
                self.mult['soumetsu-cut'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','burst']),
                self.get('res'), self.get('rdf')
            )
        hyouka_alone = {}
        for cond in self.cryo_cr:
            hyouka_alone[cond] = calc_damage(
                self.mult['hyouka'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','skill']),
                self.get('res'), self.get('rdf')
            )
        c6_charged_alone = {}
        for cond in self.cryo_cr:
            c6_charged_alone[cond] = calc_damage(
                self.mult['charged'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','charged'])+self.suigetsu_bonus,
                self.get('res'), self.get('rdf')
            )

        # apply team buffs
        self.apply_team(team)

        # soumetsu
        soumetsu_cut, soumetsu_cut_quill, soumetsu_bloom = {}, {}, {}
        for cond in self.cryo_cr:
            soumetsu_cut[cond] = calc_damage(
                self.mult['soumetsu-cut'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','burst']),
                self.get('res'), self.get('rdf')
            )
            soumetsu_cut_quill[cond] = calc_damage(
                self.mult['soumetsu-cut'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','burst']),
                self.get('res'), self.get('rdf'),
                quill = self.get('quill')
            )
            soumetsu_bloom[cond] = calc_damage(
                self.mult['soumetsu-bloom'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','burst']),
                self.get('res'), self.get('rdf')
            )
        
        # hyouka
        hyouka, hyouka_quill = {}, {}
        for cond in self.cryo_cr:
            hyouka[cond] = calc_damage(
                self.mult['hyouka'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','skill']),
                self.get('res'), self.get('rdf')
            )
            hyouka_quill[cond] = calc_damage(
                self.mult['hyouka'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','skill']),
                self.get('res'), self.get('rdf'),
                quill = self.get('quill')
            )

        # c6 charged
        c6_charged, c6_charged_quill = {}, {}
        for cond in self.cryo_cr:
            c6_charged[cond] = calc_damage(
                self.mult['charged'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','charged'])+self.suigetsu_bonus,
                self.get('res'), self.get('rdf')
            )
            c6_charged_quill[cond] = calc_damage(
                self.mult['charged'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','charged'])+self.suigetsu_bonus,
                self.get('res'), self.get('rdf'),
                quill = self.get('quill')
            )
        
        # normal attacks
        normal1, charged = {}, {}
        for cond in self.cryo_cr:
            normal1[cond] = calc_damage(
                self.mult['a1'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','normal']),
                self.get('res'), self.get('rdf')
            )
            charged[cond] = calc_damage(
                self.mult['charged'],
                self.get('atk'), self.get('cr', self.cryo_cr[cond]), self.get('cd'), self.get('bns', ['cryo','charged']),
                self.get('res'), self.get('rdf')
            )
        
        estimated_rotation = soumetsu_cut_quill['frozen']*10 + soumetsu_cut['frozen']*9 + soumetsu_bloom['frozen']
        estimated_rotation = estimated_rotation + hyouka['frozen']*2 + normal1['frozen']*3 + c6_charged['frozen']*6 + charged['frozen']*3

        self.reset_team()

        return {
            'rotation': estimated_rotation,
            'soumetsu quill': soumetsu_cut_quill['frozen'], 
            'soumetsu cut': soumetsu_cut['frozen'],
            'soumetsu alone': soumetsu_cut_alone['cryo'],
            'hyouka quill': hyouka_quill['frozen'],
            'hyouka': hyouka['frozen'],
            'hyouka alone': hyouka_alone['cryo'],
            'c6 charged quill': c6_charged_quill['frozen'],
            'c6 charged': c6_charged['frozen'],
            'c6 charged alone': c6_charged_alone['cryo'],
            'charged': charged['frozen']
            }
    
    

