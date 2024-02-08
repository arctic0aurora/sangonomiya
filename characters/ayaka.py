from archive import *
from chara import *
from artifact import *
from formation import *
from optim import *

import numpy as np

class Ayaka(CharacterBase):
    def __init__(self, weapon='mistsplitter', cryo_weight=1, frozen_weight=0.5):
        self.name = 'Ayaka'
        self.weapon = weapon
        self.cryo_weight = cryo_weight
        self.frozen_weight = frozen_weight
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
        self.attrs = self.construct_attrs(ayaka_base)
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
        self.recharge_thres = 137 # tested with favonius shenhe
        self.quill = 0
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()

    def no_cryo_cr(self):
        return 0
    
    def cryo_cr(self):
        return np.sum(self.attrs['cr-cryo'])
    
    def frozen_cr(self):
        return np.sum(self.attrs['cr-cryo']) + np.sum(self.attrs['cr-frozen'])

    def apply_weapon(self):
        if self.weapon == 'mistsplitter':
            self.apply_mistsplitter()

    def apply_mistsplitter(self):
        self.apply_modifier('atk0', 674)
        self.apply_modifier('cd', 44.1)
        self.apply_modifier('bns', 12)
        self.apply_modifier('cryo', 28)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('blizzard', 2):
            self.apply_modifier('cryo', 15)
        if self.artifacts.contains('blizzard', 4):
            self.apply_modifier('cr-cryo', 20)
            self.apply_modifier('cr-frozen', 20)
        if self.artifacts.contains('emblem', 2):
            self.apply_modifier('rcg', 20)
        self.apply_a18_artifacts()

    def apply_cryo_resonation(self):
        self.apply_modifier('cr-cryo', 15)
    
    def reset_team(self):
        super().reset_stats()
        self.apply_mistsplitter()
        self.apply_artifacts(self.artifacts)

    def apply_team(self, team):
        if 'shenhe' in team or 'ganyu' in team:
            self.apply_cryo_resonation()
        if 'kazuha' in team:
            self.apply_modifier('A', 20) # freedom-sworn            
            self.apply_modifier('res', -40) # viridescent4
            self.apply_modifier('cryo', 42) # talent
        if 'kokomi' in team:
            self.apply_modifier('A', 48) # thrilling-tales
            self.apply_modifier('A', 20) # millelith4
        if 'shenhe' in team:
            self.apply_modifier('A', 20) # noblesse4
            self.apply_modifier('res', -15) # burst
            self.apply_modifier('cryo', 15) # talent1
            self.apply_modifier('bns', 15) # talent2
            self.quill = 2513 # favonius
        if 'zhongli' in team:
            self.apply_modifier('A', 20) # millelith4
            self.apply_modifier('res', -20) # skill
    
    
    def optim_target(self, team=['kazuha', 'kokomi', 'shenhe'], args=['recharge_thres']):
        # returns full soumetsu with 10 quills as feature

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}

        conditioned_cr = {
            'no': self.no_cryo_cr,
            'cryo': self.cryo_cr,
            'frozen': self.frozen_cr,
        }

        self.apply_team(team)

        # soumetsu
        soumetsu_full = {}
        for cond in conditioned_cr:
            soumetsu_full[cond] = calc_damage(
                1.4*(19*self.mult['soumetsu-cut']+self.mult['soumetsu-bloom']), # with c2 mini seki-no-tos
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','burst']),
                self.res(), self.rdf(),
                quill = 10*self.quill
            )

        feature = soumetsu_full['frozen']*self.frozen_weight + soumetsu_full['cryo']*(self.cryo_weight-self.frozen_weight) + soumetsu_full['no']*(1-self.cryo_weight)

        self.reset_team()

        return feature, {
            'soumetsu full': soumetsu_full['frozen'], 
            }


    def additional_feature(self, team=['kazuha', 'kokomi', 'shenhe'], args=['recharge_thres']):
        # returns soumetsu and c6 charged damage

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}
        
        conditioned_cr = {
            'no': self.no_cryo_cr,
            'cryo': self.cryo_cr,
            'frozen': self.frozen_cr,
        }

        # alone without team buffs
        soumetsu_cut_alone = {}
        for cond in conditioned_cr:
            soumetsu_cut_alone[cond] = calc_damage(
                self.mult['soumetsu-cut'],
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','burst']),
                self.res(), self.rdf()
            )
        c6_charged_alone = {}
        for cond in conditioned_cr:
            c6_charged_alone[cond] = calc_damage(
                self.mult['charged'],
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','charged'])+self.suigetsu_bonus,
                self.res(), self.rdf()
            )

        # apply team buffs
        self.apply_team(team)

        # soumetsu
        soumetsu_cut, soumetsu_cut_quill = {}, {}
        for cond in conditioned_cr:
            soumetsu_cut[cond] = calc_damage(
                self.mult['soumetsu-cut'],
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','burst']),
                self.res(), self.rdf()
            )
            soumetsu_cut_quill[cond] = calc_damage(
                self.mult['soumetsu-cut'],
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','burst']),
                self.res(), self.rdf(),
                quill = self.quill
            )

        # c6 charged
        c6_charged, c6_charged_quill = {}, {}
        for cond in conditioned_cr:
            c6_charged[cond] = calc_damage(
                self.mult['charged'],
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','charged'])+self.suigetsu_bonus,
                self.res(), self.rdf()
            )
            c6_charged_quill[cond] = calc_damage(
                self.mult['charged'],
                self.atk(), self.cr()+conditioned_cr[cond](), self.cd(), self.bns(['cryo','charged'])+self.suigetsu_bonus,
                self.res(), self.rdf(),
                quill = self.quill
            )

        self.reset_team()

        return {
            'soumetsu quill': soumetsu_cut_quill['frozen'], 
            'soumetsu cut': soumetsu_cut['frozen'],
            'soumetsu alone': soumetsu_cut_alone['cryo'],
            'c6 charged quill': c6_charged_quill['frozen'],
            'c6 charged': c6_charged['frozen'],
            'c6 charged alone': c6_charged_alone['cryo'],
            }
    
    

