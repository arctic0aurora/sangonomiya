from archive import *
from chara import *
from artifact import *
from formation import *
from reaction import *
from optim import *

import numpy as np


class ClorindeV2(CharacterBase):

    def __init__(self, constellation=0, weapon='absolution', virtual_artefact='whimsy', name='Clorinde(V1)'):
        self.name = name
        self.attrs = CharacterAttrs()
        self.artifacts = ArtifactCollection([])
        self.cons = constellation
        self.weapon = weapon
        self.vartefact = virtual_artefact
        clorinde_base = {
            'hp0': 12956,
            'atk0': 337,
            'df0': 784,
            'cr': 24.2+20, # clorinde-talent2
            'cd': 50,
            'rcg': 100,
            'em': 0,
            'electro': 0,
            'em-extra': 0,
        }
        self.construct_attrs(clorinde_base)
        self.mult = {
            'hunt': 52.9 + 60, # e normal
            'hunt-pierce': 76.7 + 60, # e normal +
            'impale-night': 46.2, # e + (*3)
            'last-lightfall': 228.4, # q (*5)
            'nightwatch': 30, # c1
        }
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['any'], # for virtual artefacts
        }
        self.recharge_thres = 100 # pending test
        self.reaction = 'none' # aggravate if dendro
        self.apply_weapon()

    def apply_weapon(self):
        if self.weapon == 'absolution':
            self.apply_absolution()
        elif self.weapon == 'mistsplitter':
            self.apply_mistsplitter()
        elif self.weapon == 'haran':
            self.apply_haran(refinement=1)
        elif self.weapon == 'haran-r2':
            self.apply_haran(refinement=2)
        elif self.weapon == 'foliar':
            self.apply_foliar()
        elif self.weapon == 'jade':
            self.apply_primodial_jade()
        elif self.weapon == 'black':
            self.apply_black_sword()
    
    def apply_absolution(self):
        self.apply_modifier('atk0', 674, name='absolution')
        self.apply_modifier('cd', 64.1, name='absolution')
        self.apply_modifier('bns', 48, name='absolution')
    
    def apply_mistsplitter(self):
        self.apply_modifier('atk0', 674, name='mistsplitter')
        self.apply_modifier('cd', 44.1, name='mistsplitter')
        self.apply_modifier('bns', 12, name='mistsplitter')
        self.apply_modifier('electro', 28, name='mistsplitter')
    
    def apply_haran(self, refinement=2):
        self.apply_modifier('atk0', 608, name='haran')
        self.apply_modifier('cr', 33.1, name='haran')
        self.apply_modifier('bns', 9+3*refinement, name='haran')
        self.apply_modifier('normal', 30+10*refinement, name='haran')

    def apply_foliar(self):
        self.apply_modifier('atk0', 542, name='foliar')
        self.apply_modifier('cd', 88.2, name='foliar')
        self.apply_modifier('cr', 4, name='foliar')
        
    def apply_primodial_jade(self):
        self.apply_modifier('atk0', 542, name='primodial-jade')
        self.apply_modifier('cr', 44.1, name='primodial-jade')
        self.apply_modifier('H', 20, name='primodial-jade')
        self.apply_conversion_modifier('a', 'hp', 1.2, name='primodial-jade')
    
    def apply_black_sword(self):
        self.apply_modifier('atk0', 510, name='black-sword')
        self.apply_modifier('cr', 27.6, name='black-sword')
        self.apply_modifier('normal', 40, name='black-sword')
    
    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.vartefact == 'whimsy':
            self.apply_modifier('A', 18, name='whimsy')
            self.apply_modifier('bns', 54, name='whimsy')
        elif self.vartefact == 'echo':
            self.apply_modifier('A', 18, name='echo')
        elif self.vartefact == 'marechaussee':
            self.apply_modifier('normal', 15, name='marechaussee')
            self.apply_modifier('charged', 15, name='marechaussee')
            self.apply_modifier('cr', 36, name='marechaussee')
        elif self.vartefact == 'gladiator':
            self.apply_modifier('A', 18, name='gladiator')
            self.apply_modifier('normal', 35, name='gladiator')
        elif self.vartefact == 'gilded':
            self.apply_modifier('em', 180, name='gilded') # 2 electro + 2 misc
            self.apply_modifier('A', 14, name='gilded')
    
    def echo_mult(self):
        if self.vartefact == 'echo':
            return 35
        return 0

    def apply_dendro_resonation(self):
        self.apply_modifier('em', 100)
    
    def reset_team(self):
        super().reset_attrs()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)
    
    def apply_team(self, team):
        if self.in_team(team, 'dendro'):
            self.apply_dendro_resonation()
        if self.in_team(team, ors=['nahida', 'kirara', 'baizhu', 'yaoyao']):
            self.reaction = 'aggravate'
        # dendro
        if self.in_team(team, 'nahida'):
            self.apply_modifier('a', 144, name='evenstar')
            self.apply_modifier('em', 250, name='nahida-talent1') # 1000 em
        if self.in_team(team, 'kirara'):
            self.apply_modifier('em', 120, name='khaj-nisut') # 48000 hp
            self.apply_modifier('em', 120, name='instructor')
            self.apply_modifier('bns', 12, name='kirara-c6')
        if self.in_team(team, 'baizhu'):
            self.apply_modifier('em-extra', 40*0.01, name='baizhu-talent2-equal') # 40000 hp
            self.apply_modifier('em', 120, name='instructor')
        # misc
        if self.in_team(team, 'kazuha'):
            self.apply_modifier('A', 20, name='freedom-sworn')
            self.apply_modifier('normal', 16, name='freedom-sworn')
            self.apply_modifier('charged', 16, name='freedom-sworn')
            self.apply_modifier('plunge', 16, name='freedom-sworn')
            self.apply_modifier('electro', 42, name='kazuha-talent2') # 1050 em
            self.apply_modifier('res', -40, name='viridescent4')
        if self.in_team(team, 'sucrose'):
            self.apply_modifier('em', 50, name='sucrose-talent1')
            self.apply_modifier('em', 120, name='sucrose-talent2') # assume 600 em
            self.apply_modifier('electro', 20, name='sucrose-c6')   
            self.apply_modifier('res', -40, name='viridescent4')
        if self.in_team(team, 'yelan'):
            self.apply_modifier('A', 20, name='elegy-for-the-end')
            self.apply_modifier('em', 100, name='elegy-for-the-end')
            self.apply_modifier('bns', 25.5, name='yelan-talent2')
        if self.in_team(team, 'furina'):
            self.apply_modifier('bns', 100, name='furina-q')
        if self.in_team(team, 'beidou'):
            self.apply_modifier('res', -15, name='beidou-c6')
        # overload
        if self.in_team(team, 'chevreuse'):
            self.apply_modifier('A', 20, name='noblesse')                 
            self.apply_modifier('res', -40, name='chevreuse-talent2')
            self.apply_modifier('A', 40, name='chevreuse-talent2') 
            self.apply_modifier('pyro', 60, name='chevreuse-c6')
        if self.in_team(team, 'benette'):
            self.apply_modifier('em', 120, name='instructor')
            self.apply_modifier('a', 1111, name='benette-burst-skyward')
            self.apply_modifier('pyro', 15, name='benette-c6')
    

    def optim_target(self, team=['fischl', 'kazuha', 'nahida'], args=[]):
        # optimistic estimation: q-(e-3a)*6

        if 'recharge_thres' in args and self.rcg() < self.recharge_thres:
            return Composite(), {}

        self.apply_team(team)
   
        last_lightfall_reac = calc_damage(
            self.mult['last-lightfall'],
            self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','burst']),
            self.get('res'), reaction={self.reaction: {'em': self.get('em'), 'ex': self.get('em-extra')}}
        )
        last_lightfall_no_reac = calc_damage(
            self.mult['last-lightfall'],
            self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','burst']),
            self.get('res'), reaction={}
        )
        last_lightfall = last_lightfall_reac*2 + last_lightfall_no_reac*3

        impale_night_reac = calc_damage(
            self.mult['impale-night'],
            self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
            self.get('res'), reaction={self.reaction: {'em': self.get('em'), 'ex': self.get('em-extra')}}
        )
        impale_night_no_reac = calc_damage(
            self.mult['impale-night'],
            self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
            self.get('res'), reaction={}
        )
        impale_night = impale_night_reac + impale_night_no_reac*2

        wild_hunt_reac = calc_damage(
            self.mult['hunt-pierce'] + self.echo_mult(),
            self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
            self.get('res'), reaction={self.reaction: {'em': self.get('em'), 'ex': self.get('em-extra')}}
        )
        wild_hunt_no_reac = calc_damage(
            self.mult['hunt-pierce'] + self.echo_mult(),
            self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
            self.get('res'), reaction={}
        )
        wild_hunt = wild_hunt_reac + wild_hunt_no_reac*2

        nightwatch = Composite()
        if (self.cons >= 1):
            nightwatch_reac = calc_damage(
                self.mult['nightwatch'],
                self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
                self.get('res'), reaction={self.reaction: {'em': self.get('em'), 'ex': self.get('em-extra')}}
            )
            nightwatch_no_reac = calc_damage(
                self.mult['nightwatch'],
                self.get('atk', conversion=True), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
                self.get('res'), reaction={}
            )
            nightwatch = nightwatch_reac + nightwatch_no_reac
        
        foliar = Composite()
        if (self.weapon == 'foliar'):
            foliar_normal = calc_damage(
                120,
                self.get('em'), self.get('cr'), self.get('cd'), self.get('bns', ['electro','normal']),
                self.get('res'), reaction={}
            )
            foliar_skill = calc_damage(
                120,
                self.get('em'), self.get('cr'), self.get('cd'), self.get('bns', ['electro','skill']),
                self.get('res'), reaction={}
            )
            foliar = foliar_normal*28 # + foliar_skill*14

        feature = last_lightfall + (impale_night + wild_hunt)*7 + nightwatch*8 + foliar

        self.reset_team()

        return feature, {
            'last lightfall': last_lightfall,
            'impale night': impale_night,
            'wild hunt': wild_hunt,
            'wild hunt (1hit, aggravate)': wild_hunt_reac,
            'wild hunt (1hit, no aggravate)': wild_hunt_no_reac,
            'nightwatch': nightwatch,
            'foliar': foliar,
            }