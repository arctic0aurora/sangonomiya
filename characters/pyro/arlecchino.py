from archive import *
from chara import *
from artifact import *
from formation import *
from reaction import *
from optim import *

import numpy as np

# generate bond of life axis in a rotation
def bond_simulation(atks=18, print_sequence=True):
    # assumption: bond is counted after attack
    # axis: e...zqaaa
    sequence_default = []
    sequence_crimson = []
    decay_rate = 5.5
    decree_clear = 70 # charged
    wing_dance = 15 # burst
    crimson_moon = 25 # signature weapon

    hits = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']

    bond_dft, bond_crm = 0, 0
    bond_dft = decree_clear + wing_dance
    bond_crm = decree_clear + wing_dance + crimson_moon
    pyro_counter = 0
    for i in range(1, atks+1):
        pyro_flag = False
        #if pyro_counter == 0:
        #    pyro_flag = True
        #pyro_counter = (pyro_counter+1) % 3
        #if (i % 6 == 4):
            # a4 has 2 hits
        #    if pyro_counter == 0:
        #        pyro_flag = True # no ambiguity because only one of 2 hits can be pyro
        #    pyro_counter = (pyro_counter+1) % 3
        which_hit = hits[((i-1) % 6)]
        if which_hit in ['a1', 'a4', 'a6']:
            pyro_flag = True
        sequence_default.append({'name': which_hit, 'bond': bond_dft, 'flag': pyro_flag})
        sequence_crimson.append({'name': which_hit, 'bond': bond_crm, 'flag': pyro_flag})
        bond_dft = bond_dft * (100-decay_rate) * 0.01
        bond_crm = bond_crm * (100-decay_rate) * 0.01

    if print_sequence:
        print('bond axis with 24 atks: ')
        print('\ndefault: ')
        for i, action in enumerate(sequence_default):
            which_hit = (i % 6) + 1
            print('{}{}: bond={:.1f}'.format(action['name'], '(pyro)' if action['flag'] else '', action['bond']))
        print('\ncrimson: ')
        for i, action in enumerate(sequence_crimson):
            which_hit = (i % 6) + 1
            print('{}{}: bond={:.1f}'.format(action['name'], '(pyro)' if action['flag'] else '', action['bond']))
        print('')

    return {'default': sequence_default, 'crimson': sequence_crimson}


class ArlecchinoV0(CharacterBase):

    bond_sequence = {
        'default': [],
        'crimson': []
    }

    def __init__(self, weapon='crimson', virtual_artefact='bond'):
        self.name = 'Arlecchino'
        self.weapon = weapon
        self.vartefact = virtual_artefact
        arlecchino_base = {
            'hp0': 12103,
            'atk0': 342,
            'df0': 765,
            'cr': 5,
            'cd': 88.4,
            'rcg': 100,
            'em': 0,
            'pyro': 40, # arlecchino normal
        }
        self.attrs = self.construct_attrs(arlecchino_base)
        self.mult = {
            'a1': 93.2, # normal
            'a2': 102.2,
            'a3': 128.2,
            'a4': 70.4, # a4 has 2 hits
            'a5': 140,
            'a6': 167.7,
            'charged': 256.3,
            'balemoon': 26.7, # skill
            'slash': 240.4,
            'decree': 38.4,
            'dance': 666.7, # burst
            'calamity': 900, # c2
        }
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['any'], # for virtual artefacts
        }
        self.recharge_thres = 100 # pending test
        self.reaction = 'none'
        self.sequence = self.bond_sequence['default']
        self.artifacts = ArtifactCollection([])
        self.apply_weapon()
        # self.apply_team()

    def apply_weapon(self):
        if self.weapon == 'crimson':
            self.apply_crimson()
        elif self.weapon == 'sand':
            self.apply_scarlet_sand()
        elif self.weapon == 'hpy': # primodial jade spear
            self.apply_hpy()

    def apply_crimson(self):
        self.sequence = self.bond_sequence['crimson']
        self.apply_modifier('atk0', 674)
        self.apply_modifier('cr', 22.1)
        self.apply_modifier('bns', 32)

    def apply_scarlet_sand(self):
        self.apply_modifier('atk0', 542)
        self.apply_modifier('cr', 44.1)

    def sand_atk(self):
        if self.weapon == 'sand':
            return (0.52 + 0.28*1) * self.em()
        return 0
    
    def apply_hpy(self, refinement=2):
        self.apply_modifier('atk0', 674)
        self.apply_modifier('cr', 22.1)
        self.apply_modifier('A', 7*(2.5+0.7*refinement))
        self.apply_modifier('bns', 9+3*refinement)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.vartefact == 'bond':
            self.apply_modifier('A', 18)
            self.apply_modifier('bns', 54)
        elif self.vartefact == 'echo':
            self.apply_modifier('A', 18)
        elif self.vartefact == 'marechaussee':
            self.apply_modifier('normal', 15)
            self.apply_modifier('charged', 15)
            self.apply_modifier('cr', 36)
        elif self.vartefact == 'gladiator':
            self.apply_modifier('A', 18)
            self.apply_modifier('normal', 35)
    
    def echo_mult(self):
        if self.vartefact == 'echo':
            return 35
        return 0

    def apply_pyro_resonation(self):
        self.apply_modifier('A', 25)

    def bond_atk(self, bond):
        return (2.38 * bond * 0.01 * np.sum(self.attrs['atk0']))
    
    def bond_mult(self, bond):
        return (2.38 * bond)
    
    def reset_team(self):
        super().reset_stats()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)

    def apply_team(self, team):
        if 'benette-noblesse' in team or 'benette-instructor' in team or 'chevreuse' in team:
            self.apply_pyro_resonation()
        if 'yelan' in team or 'xingqiu' in team or 'furina' in team:
            self.reaction = 'amplify'
        if 'kazuha' in team:
            # kazuha in this team may need xiphos instead of freedom-sworn          
            self.apply_modifier('res', -40) # viridescent4
            self.apply_modifier('pyro', 40) # talent
        if 'yelan' in team:
            self.apply_modifier('bns', 28) # talent average
        if 'furina' in team:
            self.apply_modifier('bns', 100) # burst
        if 'chevreuse' in team:
            self.apply_modifier('A', 20) # noblesse                  
            self.apply_modifier('res', -40) # talent1
            self.apply_modifier('A', 40) # talent2  
            self.apply_modifier('pyro', 60) # c6
        if 'benette-noblesse' in team:
            self.apply_modifier('A', 20) # noblesse
            self.apply_modifier('a', 1111) # burst (using skyward)
            self.apply_modifier('pyro', 15) # c6
        if 'benette-instructor' in team:
            self.apply_modifier('em', 120) # instructor
            self.apply_modifier('a', 1111) # burst (using skyward)
            self.apply_modifier('pyro', 15) # c6
        if 'zhongli' in team:
            self.apply_modifier('em', 120) # instructor
            self.apply_modifier('res', -20) # skill
    
    
    def optim_target(self, team=['yelan', 'xingqiu', 'zhongli'], args=[]):
        # returns full rotation damage as feature

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}

        self.apply_team(team)

        normal_cumulative = Composite()
        '''
        for action in self.sequence:
            action_result = calc_damage(
                self.mult[action['name']] + self.bond_mult(action['bond']) + self.echo_mult(),
                self.atk()+self.bond_atk(action['bond'])+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','normal']),
                self.res(), reaction={self.reaction: self.em()} if action['flag'] else {}
            )
            if action['name'] == 'a4':
                # this hit of a4 is definitely not one with elemental infusion
                extra_result = calc_damage(
                    self.mult[action['name']] + self.bond_mult(action['bond']) + self.echo_mult(),
                    self.atk()+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','normal']),
                    self.res(), reaction={}
                )
                action_result = action_result + extra_result
            normal_cumulative = normal_cumulative + action_result
        '''
        for action in self.sequence:
            action_result = calc_damage(
                self.mult[action['name']] + self.echo_mult(),
                self.atk()+self.bond_atk(action['bond'])+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','normal']),
                self.res(), reaction={self.reaction: self.em()} if action['flag'] else {}
            )
            if action['name'] == 'a4':
                # this hit of a4 is definitely not one with elemental infusion
                extra_result = calc_damage(
                    self.mult[action['name']] + self.echo_mult(),
                    self.atk()+self.bond_atk(action['bond'])+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','normal']),
                    self.res(), reaction={}
                )
                action_result = action_result + extra_result
            normal_cumulative = normal_cumulative + action_result
        
        wing_dance = calc_damage(
            self.mult['dance'],
            self.atk()+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','burst']),
            self.res(), reaction={self.reaction: self.em()}
        )

        slash = calc_damage(
            self.mult['slash'],
            self.atk()+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','skill']),
            self.res(), reaction={self.reaction: self.em()}
        )

        charged = calc_damage(
            self.mult['charged'],
            self.atk()+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','charged']),
            self.res(), reaction={self.reaction: self.em()}
        )

        feature = normal_cumulative + wing_dance + slash + charged

        self.reset_team()

        return feature, {           
            'feast full': normal_cumulative,
            'wing dance': wing_dance,
            'bloodfire slash': slash,
            'charged': charged,
            }


    def additional_feature(self, team=['yelan', 'xingqiu', 'zhongli'], args=[]):
        # returns a1

        self.apply_team(team)

        a1_vaporize = calc_damage(
            self.mult['a1'] + self.echo_mult(),
            self.atk()+self.bond_atk(self.sequence[0]['bond'])+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','normal']),
            self.res(), reaction={self.reaction: self.em()}
        )
        a1 = calc_damage(
            self.mult['a1'] + self.echo_mult(),
            self.atk()+self.bond_atk(self.sequence[0]['bond'])+self.sand_atk(), self.cr(), self.cd(), self.bns(['pyro','normal']),
            self.res(), reaction={}
        )

        self.reset_team()
        
        return {
            'first a1 vaporize': a1_vaporize,
            'first a1': a1,
            }
    
    

