from archive import *
from chara import *
from artifact import *
from attributes import *
from formation import *
from optim import *

import numpy as np


# generate fanfare/duckweed axis in a rotation
def fanfare_simulation(print_sequence=True):
    # assumption: fanfare is counted after summons attack, healing is instant to regenerate lost hp
    # (so that each time a summon consumes hp, fanfare is added twice)

    small_hp, medium_hp, large_hp = 1.6, 2.4, 3.6
    # 119 frame = 1.19s
    small_cd, medium_cd, large_cd = 119, 290, 480
    global_cd = 50 # applied only to small

    scd, mcd, lcd, gcd = 0, 0, 0, 0 # cd counters
    sequence = []
    fanfare = 100
    for i in range(0, 1800):
        # small
        if scd < 1 and gcd < 1:
            sequence.append({
                'type': 'small',
                'timer': i,
                'fanfare': fanfare,
            })
            fanfare += small_hp * 4 * 3.5 * 2
            scd, gcd = small_cd, global_cd
        if mcd < 1:
            sequence.append({
                'type': 'medium',
                'timer': i,
                'fanfare': fanfare,
            })
            fanfare += medium_hp * 4 * 3.5 * 2
            mcd, gcd = medium_cd, global_cd
        if lcd < 1:
            sequence.append({
                'type': 'large',
                'timer': i,
                'fanfare': fanfare,
            })
            fanfare += large_hp * 4 * 3.5 * 2
            lcd, gcd = large_cd, global_cd
        scd = scd - 1
        mcd = mcd - 1
        lcd = lcd - 1
        gcd = gcd - 1

    # simulation result
    # small 15 (0-400:3, 400-800:4, 800-1600:8)
    # medium 7 (1, 2, 4)
    # large 4 (1, 1, 2)
    if print_sequence:
        print('\n--- fanfare axis in 1800 frames (18.0s) ---')
        cnts = {'small':0, 'medium':0, 'large':0}
        for action in sequence:
            cnts[action['type']] += 1
            print('{}: {}, fanfare={:.1f}'.format(action['timer'], action['type'], action['fanfare']))
        print('action summary')
        for typ in cnts:
            print('{}: {} times'.format(typ, cnts[typ]))
        print('')
    return sequence


class Furina(CharacterBase):

    fanfare_sequence = []

    def __init__(self, weapon='jade', rejoice_weight=0.8, duckweed_weight=0.5):
        self.name = 'Furina'
        self.attrs = CharacterAttrs()
        self.artifacts = ArtifactCollection([])
        self.weapon = weapon
        self.rejoice_weight = rejoice_weight
        self.duckweed_weight = duckweed_weight
        furina_base = {
            'hp0': 15307,
            'atk0': 244,
            'df0': 696,
            'cr': 24.2,
            'cd': 50,
            'rcg': 100,
            'em': 0,
        }
        self.construct_attrs(furina_base)
        self.mult = {
            'solitaire-bubble': 14.2, # ousia e release
            'small': 5.82, # surintendante chevalmarin
            'medium': 10.73, # gentilhomme usher
            'large': 14.92, # mademoiselle crabaletta
            'rejoice': 20.5, # q release
            'love-chalice': 18, # furina c6
            'love-chalice-pneuma': 25, # furina c6 pneuma
        }
        self.requirement = {
            'set-type': '4pcs',
            'set-restriction': ['goldentroupe'],
        }
        self.recharge_thres = 155 # randomly set in favor of recharge hourglass
        self.apply_weapon()

    # furina talent2
    def confession_bonus(self, fanfare=0):
        if fanfare <= 400:
            return min(28, (self.get('hp')) * 0.7/1000)
        return min(28, (self.get('hp')+self.fanfare_hp(fanfare)) * 0.7/1000)
    
    # fanfare to buff
    def fanfare_bonus(self, fanfare):
        return 0.25 * min(fanfare, 400)
    
    def fanfare_hp_percent(self, fanfare):
        return max(0, 0.35 * (min(fanfare, 800) - 400))
    
    def fanfare_hp(self, fanfare):
        return 0.01 * self.fanfare_hp_percent(fanfare) * self.get('hp0')
    
    def apply_weapon(self):
        if self.weapon == 'tranquil':
            self.apply_tranquil()
        elif self.weapon == 'misugiri':
            self.apply_misugiri()
        elif self.weapon == 'jade':
            self.apply_primodial_jade()
        elif self.weapon == 'favonius':
            self.apply_favonius()
    
    def apply_tranquil(self):
        self.apply_modifier('atk0', 542, name='tranquil')
        self.apply_modifier('cd', 88.2, name='tranquil')
        self.apply_modifier('H', 28, name='tranquil')
        self.apply_modifier('skill', 24, name='tranquil')

    def apply_misugiri(self, geo=False):
        self.apply_modifier('atk0', 542, name='misugiri')
        self.apply_modifier('cd', 88.2, name='misugiri')
        self.apply_modifier('normal', 16, name='misugiri')
        self.apply_modifier('skill', 24, name='misugiri')
        self.apply_modifier('D', 20, name='misugiri')
        if geo:
            self.apply_modifier('skill', 24, name='misugiri-geo')

    def apply_primodial_jade(self):
        self.apply_modifier('atk0', 542, name='primodial-jade')
        self.apply_modifier('cr', 44.1, name='primodial-jade')
        self.apply_modifier('H', 20, name='primodial-jade')
    
    def jade_atk(self):
        return (0.012 * self.get('hp'))

    def apply_favonius(self):
        self.apply_modifier('atk0', 454, name='favonius')
        self.apply_modifier('rcg', 61.3, name='favonius')

    def apply_artifacts(self, artifacts):
        super().apply_artifacts(artifacts)
        if self.artifacts.contains('goldentroupe', 2):
            self.apply_modifier('skill', 25, name='golden-troupe2')
        if self.artifacts.contains('goldentroupe', 4):
            self.apply_modifier('skill', 50, name='golden-troupe4')
        if self.artifacts.contains('emblem', 2):
            self.apply_modifier('rcg', 20, name='emblem2')
        self.apply_h20_artifacts()
        for artifact_set in ['depth', 'nymph']:
            if self.artifacts.contains(artifact_set, 2):
                self.apply_modifier('hydro', 15, name='hydro15-set2')

    def apply_hydro_resonation(self):
        self.apply_modifier('H', 25, name='hydro-resonation')
    
    def reset_team(self):
        super().reset_attrs()
        self.apply_weapon()
        self.apply_artifacts(self.artifacts)

    def apply_team(self, team=[]):
        if self.in_team(team, ors=['kokomi', 'yelan', 'xingqiu', 'ayato']):
            self.apply_hydro_resonation()
        if self.in_team(team, 'kazuha'):
            self.apply_modifier('A', 20, name='freedom-sworn')
            self.apply_modifier('normal', 16, name='freedom-sworn')
            self.apply_modifier('charged', 16, name='freedom-sworn')
            self.apply_modifier('plunge', 16, name='freedom-sworn')       
            self.apply_modifier('hydro', 42, name='kazuha-talent2')
        if self.in_team(team, ors=['kazuha', 'lynette', 'jean', 'xianyun']):          
            self.apply_modifier('res', -40, name='viridescent4')
        if self.in_team(team, 'yelan'):
            # self.apply_modifier('bns', 28, name='yelan-talent2')
            self.apply_modifier('bns', 0, name='yelan-talent2') # no buff for off-field
        if self.in_team(team, 'xingqiu'):
            self.apply_modifier('res', -15, name='xingqiu-c2')


    def optim_target(self, team=['kazuha', 'kokomi', 'yelan'], args=['recharge_thres']):
        # returns mademoiselle crabaletta damage as feature

        if 'recharge_thres' in args and self.get('rcg') < self.recharge_thres:
            return Composite(), {}
        
        self.apply_team(team)
        
        # mademoiselle crabaletta
        large_initial = calc_damage(
            self.mult['large'],
            self.get('hp'), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.get('res')
        )
        
        large_rejoice = calc_damage(
            self.mult['large'],
            self.get('hp'), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(400)+self.confession_bonus(400),
            self.get('res')
        )
        
        large_duckweed = calc_damage(
            self.mult['large'],
            self.get('hp')+self.fanfare_hp(800), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(800)+self.confession_bonus(800),
            self.get('res')
        )
        
        feature = large_duckweed*self.duckweed_weight + large_rejoice*(self.rejoice_weight-self.duckweed_weight) + large_initial*(1-self.rejoice_weight)
        
        self.reset_team()

        return feature, {}
    

    def additional_feature(self, team=['kazuha', 'kokomi', 'yelan'], args=['recharge_thres']):
        # returns rotation damage q+e 18s

        self.apply_team(team)

        # elemental burst
        rejoice = calc_damage(
            self.mult['rejoice'],
            self.get('hp'), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','burst'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.get('res')
        )
        
        # elemental skill release
        bubble = calc_damage(
            self.mult['solitaire-bubble'],
            self.get('hp'), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.get('res')
        )
        
        # calculate 3 summons with unit damage
        unit_initial = calc_damage(
            1,
            self.get('hp'), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(100)+self.confession_bonus(100),
            self.get('res')
        )
        
        unit_rejoice = calc_damage(
            1,
            self.get('hp'), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(400)+self.confession_bonus(400),
            self.get('res')
        )
        
        unit_duckweed = calc_damage(
            1,
            self.get('hp')+self.fanfare_hp(800), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(800)+self.confession_bonus(800),
            self.get('res')
        )

        salon_cumulative = Composite()
        for action in Furina.fanfare_sequence:
            action_result = calc_damage(
                self.mult[action['type']],
                self.get('hp')+self.fanfare_hp(action['fanfare']), self.get('cr'), self.get('cd'), self.get('bns', ['hydro','skill'])+self.fanfare_bonus(action['fanfare'])+self.confession_bonus(action['fanfare']),
                self.get('res')
            )
            salon_cumulative = salon_cumulative + action_result
        
        self.reset_team()

        return {
            'rotation total': rejoice+bubble+salon_cumulative,
            'salon solitaire total': salon_cumulative,
            'rejoice': rejoice,
            'ousia bubble': bubble,
            'surintendante chevalmarin(initial)': unit_initial*self.mult['small'],
            'surintendante chevalmarin(rejoice)': unit_rejoice*self.mult['small'],
            'surintendante chevalmarin(duckweed)': unit_duckweed*self.mult['small'],
            'gentilhomme usher(initial)': unit_initial*self.mult['medium'],
            'gentilhomme usher(rejoice)': unit_rejoice*self.mult['medium'],
            'gentilhomme usher(duckweed)': unit_duckweed*self.mult['medium'],
            'mademoiselle crabaletta(initial)': unit_initial*self.mult['large'],
            'mademoiselle crabaletta(rejoice)': unit_rejoice*self.mult['large'],
            'mademoiselle crabaletta(duckweed)': unit_duckweed*self.mult['large'],
            }







