from archive import *

import functools


@functools.total_ordering
class TimedAttr():
    def __init__(self, value=0, t0=0, t1=65535, name=''):
        self.value = value
        self.t0 = t0
        self.t1 = t1
        self.name = name
    
    # calculations
    def __add__(self, a):
        if isinstance(a, TimedAttr):
            return TimedAttr(self.value + a.value)
        else:
            return TimedAttr(self.value + a)
    
    def __radd__(self, a):
        return a + self.value
    
    def __iadd__(self, num):
        return TimedAttr(self.value + num)

    def __mul__(self, num):
        return TimedAttr(self.value * num)
    
    def __imul__(self, num):
        return TimedAttr(self.value * num)

    def __str__(self):
        if self.t1 > 65535-1:
            return "{}({:.1f})".format(self.name, self.value)
        return "{}({:.1f}, from {:.1f} to {:.1f})".format(self.name, self.value, self.t0, self.t1)

    # lesser than
    def __lt__(self, a):
        return (self.value < a.value)
    
    def range_contains(self, t) -> bool:
        return (t > self.t0-0.001 and t < self.t1+0.001)


class CharacterAttrs():
    def __init__(self):
        self.ls = {} # attributes: {'atk': [311, ...]}
        self.cv = {} # conversions: {'atk':{'hp':[0.01, ...]}}
    
    def construct_list(self, params={}):
        for key, value in params.items():
            self.ls[key] = [TimedAttr(value, name='initial')]
        
    def append_modifier(self, attr, value=0, t0=0, t1=65535, name=''):
        if attr not in self.ls:
            self.ls[attr] = [TimedAttr(0, name='initial')]
        self.ls[attr].append(TimedAttr(value, t0, t1, name))
    
    def append_conversion(self, attr, from_attr, rate=0, t0=0, t1=65535, name=''):
        if attr not in self.cv:
            self.cv[attr] = {from_attr: [TimedAttr(0, t0, t1, name='initial')]}
        elif from_attr not in self.cv[attr]:
            self.cv[attr][from_attr] = [TimedAttr(0, t0, t1, name='initial')]
        self.cv[attr][from_attr].append(TimedAttr(rate, t0, t1, name))
    
    def reset_list(self):
        for attr in self.ls:
            self.ls[attr] = self.ls[attr][:1]
        for attr in self.cv:
            for from_attr in self.cv[attr]:
                self.cv[attr][from_attr] = self.cv[attr][from_attr][:1]
    
    def contains(self, attr):
        return attr in self.ls

    def filter_attr(self, attr, t=-1):
        if t < 0:
            return self.ls[attr]
        return [item for item in self.ls[attr] if item.range_contains(t)]
    
    def filter_conv(self, attr, from_attr, t=-1):
        if t < 0:
            return self.cv[attr][from_attr]
        return [item for item in self.cv[attr][from_attr] if item.range_contains(t)]
    
    def get_attr(self, primary_attr, secondary_attrs=[], conversion=False, t=-1):
        primus = sum(self.filter_attr(primary_attr), 0)
        secondus = 0
        for attr in secondary_attrs:
            secondus += sum(self.filter_attr(attr, t), 0)
        tertius = 0
        if conversion and primary_attr in self.cv:
            for from_attr in self.cv[primary_attr]:
                tertius += self.get_attr_wrapper(from_attr, conversion=False, t=t) * 0.01 * sum(self.filter_conv(primary_attr, from_attr, t), 0)
        return primus + secondus + tertius
    
    def get_attr_complex(self, attr, conversion=False, t=-1):
        if attr == 'hp':
            return self.get_attr('hp0', t=t) * (1+0.01*self.get_attr('H', t=t)) + self.get_attr('h', t=t, conversion=conversion)
        elif attr == 'atk':
            return self.get_attr('atk0', t=t) * (1+0.01*self.get_attr('A', t=t)) + self.get_attr('a', t=t, conversion=conversion)
        elif attr == 'df':
            return self.get_attr('df0', t=t) * (1+0.01*self.get_attr('D', t=t)) + self.get_attr('d', t=t, conversion=conversion)
        elif attr == 'spd':
            return self.get_attr('spd0', t=t) * (1+0.01*self.get_attr('S', t=t)) + self.get_attr('s', t=t, conversion=conversion)
        return 0

    def get_attr_wrapper(self, attr, secondary_attrs=[], conversion=False, t=-1):
        if attr in ['hp', 'atk', 'df', 'spd']:
            return self.get_attr_complex(attr, conversion, t)
        return self.get_attr(attr, secondary_attrs, conversion, t)

    def print(self, params=SangonomiyaArchive.genshin_panel):
        print('--- attributes ---')
        for attr in params:
            value = self.get_attr_wrapper(attr, conversion=True)
            if value != 0:
                print('[{}: {:.1f}]'.format(SangonomiyaArchive.attr_name.get(attr, attr), value))
    
    def print_all(self, params=SangonomiyaArchive.genshin_panel):
        self.print(params)
        print('\n--- detailed information ---')
        for attr in self.ls:
            value = self.get_attr_wrapper(attr, conversion=True)
            if value != 0:
                for i, item in enumerate(self.ls[attr]):
                    if i == 0:
                        print('[{}] {}'.format(SangonomiyaArchive.attr_name.get(attr, attr), item))
                    else:
                        print('+ {}'.format(item))
                if attr in self.cv:
                    for from_attr in self.cv[attr]:
                        for i, item in enumerate(self.cv[attr][from_attr]):
                            if i == 0:
                                print('[{} from {}] {}'.format(SangonomiyaArchive.attr_name.get(attr, attr), SangonomiyaArchive.attr_name.get(from_attr, from_attr), item))
                            else:
                                print('+ {}'.format(item))



