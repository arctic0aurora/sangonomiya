from archive import *
from chara import *
from artifact import *
from formation import *
from reaction import *
from optim import *

import numpy as np

# arlecchino for beta v3, need update

# generate bond of life axis in a rotation
def bond_simulation(axis='e-q1-e-z0-a4-a4-a4-a4', vapor_rate=1.0, print_sequence=True):
    # assumption: bond is counted after attack
    seq = [] 
    bond_dft, bond_crm = 0, 0 # default, crimson
    decay_rate = 6.5
    decree_flag, crimson_flag = False, True
    decree_clear_instant = 40
    decree_clear_wait = 70
    decree_clear_full = 80
    crimson_moon = 18 # signature weapon

    hits = ['a1', 'a2', 'a3', 'a41', 'a42', 'a5', 'a6']
    pyro_list = ['a1', 'a41', 'a6']
    if vapor_rate < 0.7:
        pyro_list = ['a41', 'a6']
    if vapor_rate < 0.4:
        pyro_list = ['a6']
    if vapor_rate < 0.1:
        pyro_list = []
   
    actions = axis.split('-')

    for ac in actions:
        if ac == 'e':
            decree_flag = True
            seq.append({'name': ac, 'bond': bond_dft, 'bond-crm': bond_crm, 'pyro': True})
        elif ac in ['q0', 'q1']: 
            seq.append({'name': ac, 'bond': bond_dft, 'bond-crm': bond_crm, 'pyro': True})
            bond_dft, bond_crm = 0, 0
            if ac == 'q0' and decree_flag:
                bond_dft += decree_clear_instant
                bond_crm += decree_clear_instant
            elif ac == 'q1' and decree_flag:
                bond_dft += decree_clear_wait
                bond_crm += decree_clear_wait
            decree_flag = False
        elif ac in ['z0', 'z1']:
            seq.append({'name': ac, 'bond': bond_dft, 'bond-crm': bond_crm, 'pyro': True})
            if ac == 'z0' and decree_flag:
                bond_dft += decree_clear_instant
                bond_crm += decree_clear_instant
            elif ac == 'z1' and decree_flag:
                bond_dft += decree_clear_wait
                bond_crm += decree_clear_wait
            if crimson_flag:
                bond_crm += crimson_moon
                crimson_flag = False
            decree_flag = False
        elif ac == 'a4':
            for normal in hits[0:5]:
                pyro_infusion = True if normal in pyro_list else False
                seq.append({'name': normal, 'bond': bond_dft, 'bond-crm': bond_crm, 'pyro': pyro_infusion})
                bond_dft = bond_dft * (1-0.01*decay_rate)
                bond_crm = bond_crm * (1-0.01*decay_rate)
        elif ac == 'a6':
            for normal in hits[0:7]:
                pyro_infusion = True if normal in pyro_list else False
                seq.append({'name': normal, 'bond': bond_dft, 'bond-crm': bond_crm, 'pyro': pyro_infusion})
                bond_dft = bond_dft * (1-0.01*decay_rate)
                bond_crm = bond_crm * (1-0.01*decay_rate)
        
    if print_sequence:
        print('\n--- arlecchino bond axis ---')
        for item in seq:
            print('{}{}: bond = {:.1f}/{:.1f}'.format(item['name'], '(pyro)' if item['pyro'] else '', item['bond'], item['bond-crm']))
    
    return seq


class ArlecchinoV3(CharacterBase):

    bond_sequence = []

    axis_maxima = 'e-q1-e-z0-a4-a4-a4-a4'
    axis_extend = 'e-q1-e-a4-a4-z1-a4-a4'

    def __init__(self, constellation=0, weapon='crimson', virtual_artefact='whimsy'):
        self.name = 'Arlecchino(v3)'
        self.attrs = CharacterAttrs()
        self.artifacts = ArtifactCollection([])
        self.cons = constellation
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
            'pyro': 0,
            'praise-shadow': 40, # arlecchino normal
        }
        self.construct_attrs(arlecchino_base)
        self.normal_interval = 0.55 # 3.3s for 6 hits
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
        self.apply_weapon()

    def apply_weapon(self):
        if self.weapon == 'crimson':
            self.apply_crimson()
        elif self.weapon == 'sand':
            self.apply_scarlet_sand()
        elif self.weapon == 'hpy': # primodial jade spear
            self.apply_hpy()
        elif self.weapon == 'fjord':
            self.apply_ballad_fjord()

    def apply_crimson(self):
        self.apply_modifier('atk0', 674, name='crimson-moon')
        self.apply_modifier('cr', 22.1, name='crimson-moon')
        self.apply_modifier('bns', 12, name='crimson-moon')
        self.apply_modifier('praise-shadow', 20, name='crimson-moon')

    def apply_scarlet_sand(self):
        self.apply_modifier('atk0', 542, name='scarlet-sand')
        self.apply_modifier('cr', 44.1, name='scarlet-sand')

    def sand_atk(self, t, team):
        if self.weapon == 'sand':
            if t < 1 + 10.01:
                return (0.52 + 0.28*1) * (self.em() + self.instructor_em(t, team) + self.sucrose_em(t, team, flag='sand'))
            else:
                return (0.52 + 0.28*0) * (self.em() + self.instructor_em(t, team) + self.sucrose_em(t, team, flag='sand'))
        return 0
    
    def apply_hpy(self, refinement=1):
        self.apply_modifier('atk0', 674)
        self.apply_modifier('cr', 22.1)
        self.apply_modifier('A', 7*(2.5+0.7*refinement))
        self.apply_modifier('bns', 9+3*refinement)
    
    def apply_ballad_fjord(self, refinement=5):
        self.apply_modifier('atk0', 510)
        self.apply_modifier('cr', 27.6)
        self.apply_modifier('em', 90+30*refinement)

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.vartefact == 'whimsy':
            self.apply_modifier('A', 18)
            self.apply_modifier('praise-shadow', 54)
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
        if 'kazuha-freedom' in team:
            self.apply_modifier('A', 20) # freedom-sworn
            self.apply_modifier('normal', 16) # freedom-sworn
            self.apply_modifier('charged', 16) # freedom-sworn
            self.apply_modifier('plunge', 16) # freedom-sworn
            self.apply_modifier('res', -40) # viridescent4
            self.apply_modifier('pyro', 40) # talent
        if 'sucrose' in team:
            self.apply_modifier('A', 48) # thrilling-tale
        if 'yelan' in team:
            self.apply_modifier('A', 20) # elegy
            self.apply_modifier('em', 100) # elegy
            # self.apply_modifier('bns', 28) # implemented in yelan_bonus
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
            # self.apply_modifier('em', 120) # instructor
            self.apply_modifier('a', 1111) # burst (using skyward)
            self.apply_modifier('pyro', 15) # c6
        if 'zhongli-millilith' in team:
            self.apply_modifier('A', 20) # instructor
            self.apply_modifier('res', -20) # skill
        if 'zhongli-instructor' in team:
            # self.apply_modifier('em', 120) # instructor
            self.apply_modifier('res', -20) # skill
    
    def yelan_bonus(self, t, team=['yelan']):
        if 'yelan' in team and t < 4 + 15.01:
            return min(1+3.5*t, 50)
        return 0
    
    def instructor_em(self, t, team=['zhongli-instructor']):
        if 'benette-instructor' in team or 'zhongli-instructor' in team:
            if t < 5.5 + 8.01:
                return 120
        return 0
    
    def sucrose_em(self, t, team=['sucrose'], flag='none'):
        if 'sucrose' in team and t < 7 + 8.01:
            if flag == 'sand':
                return 50
            return 50 + 720 * 0.2
        return 0
    
    
    def optim_target(self, team=['yelan', 'xingqiu', 'zhongli'], args=[]):
        # returns full rotation damage as feature

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}

        self.apply_team(team)

        normal_cumulative = Composite()
        for t, action in enumerate(self.sequence):
            global_t = 10 + t*self.normal_interval
            action_result = calc_damage(
                self.mult[action['name']] + self.bond_mult(action['bond']) + self.echo_mult(),
                self.atk()+self.sand_atk(global_t, team), self.cr(), self.cd(), self.bns(['pyro','normal','praise-shadow'])+self.yelan_bonus(global_t, team),
                self.res(), reaction={self.reaction: {'em': self.em()+self.instructor_em(global_t, team)+self.sucrose_em(global_t, team)}} if action['flag'] else {}
            )
            if action['name'] == 'a4':
                # this hit of a4 is definitely not one with elemental infusion
                extra_result = calc_damage(
                    self.mult[action['name']] + self.bond_mult(action['bond']) + self.echo_mult(),
                    self.atk()+self.sand_atk(global_t, team), self.cr(), self.cd(), self.bns(['pyro','normal','praise-shadow'])+self.yelan_bonus(global_t, team),
                    self.res(), reaction={}
                )
                action_result = action_result + extra_result
            normal_cumulative = normal_cumulative + action_result
        
        wing_dance = calc_damage(
            self.mult['dance'],
            self.atk()+self.sand_atk(8, team), self.cr(), self.cd(), self.bns(['pyro','burst','praise-shadow'])+self.yelan_bonus(8, team), # at t=3 to t=5
            self.res(), reaction={self.reaction: {'em': self.em()+self.instructor_em(8, team)+self.sucrose_em(8, team)}}
        )

        slash = calc_damage(
            self.mult['slash'],
            self.atk()+self.sand_atk(21, team), self.cr(), self.cd(), self.bns(['pyro','skill']),
            self.res(),
        )

        charged = calc_damage(
            self.mult['charged'],
            self.atk()+self.sand_atk(7, team), self.cr(), self.cd(), self.bns(['pyro','charged'])+self.yelan_bonus(7, team), # at t=2 to t=3
            self.res(), reaction={self.reaction: {'em': self.em()+self.instructor_em(7, team)+self.sucrose_em(7, team)}}
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
        # returns all normal damage

        self.apply_team(team)

        normal_list = {}
        for t, action in enumerate(self.sequence):
            global_t = 10 + t*self.normal_interval
            action_result = calc_damage(
                self.mult[action['name']] + self.bond_mult(action['bond']) + self.echo_mult(),
                self.atk()+self.sand_atk(global_t, team), self.cr(), self.cd(), self.bns(['pyro','normal','praise-shadow'])+self.yelan_bonus(global_t, team),
                self.res(), reaction={self.reaction: {'em': self.em()+self.instructor_em(global_t, team)+self.sucrose_em(global_t, team)}} if action['flag'] else {}
            )
            normal_list['{}-{}'.format(t, action['name'])] = action_result
            if action['name'] == 'a4':
                # this hit of a4 is definitely not one with elemental infusion
                extra_result = calc_damage(
                    self.mult[action['name']] + self.bond_mult(action['bond']) + self.echo_mult(),
                    self.atk()+self.sand_atk(global_t, team), self.cr(), self.cd(), self.bns(['pyro','normal','praise-shadow'])+self.yelan_bonus(global_t, team),
                    self.res(), reaction={}
                )
                normal_list['{}-a4-2'.format(t)] = extra_result

        self.reset_team()
        
        return normal_list
    

if __name__ == '__main__':
    bond_simulation()

