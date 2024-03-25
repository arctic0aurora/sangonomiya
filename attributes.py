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
    
    def __iadd__(self, num):
        return TimedAttr(self.value + num)

    def __mul__(self, num):
        return TimedAttr(self.value * num)
    
    def __imul__(self, num):
        return TimedAttr(self.value * num)

    def __str__(self):
        return "{}({:.1f}, from {:.1f} to {:.1f})".format(self.name, self.value, self.t0, self.t1)

    # lesser than
    def __lt__(self, a):
        return (self.value < a.value)
    
    def range_contains(self, t) -> bool:
        return (t > self.t0-0.001 and t < self.t1+0.001)


class CharacterAttrs():
    def __init__(self):
        self.ls = {}
    
    def construct_list(self, params={}):
        for key, value in params.items():
            self.ls[key] = [TimedAttr(value, name='initial')]
        
    def append_modifier(self, attr, value=0, t0=0, t1=65535, name=''):
        if attr not in self.ls:
            self.ls[attr] = [TimedAttr(0, name='initial')]
        self.ls[attr].append(TimedAttr(value, t0, t1, name))
    
    def reset_list(self):
        for attr in self.ls:
            self.ls[attr] = self.ls[attr][:1]
    
    def contains(self, attr):
        return attr in self.ls

    def filter_attr(self, attr, t=-1):
        if t < 0:
            return self.ls[attr]
        return [item for item in self.ls[attr] if item.range_contains(t)]
    
    def get_attr(self, primary_attr, secondary_attrs=[], t=-1):
        primus = sum(self.filter_attr(primary_attr), TimedAttr(0)).value
        secondus = 0
        for attr in secondary_attrs:
            secondus += sum(self.filter_attr(attr), TimedAttr(0)).value
        return primus + secondus
    
    def get_attr_complex(self, attr, t=-1):
        if attr == 'hp':
            return self.get_attr('hp0', t=t) * (1+0.01*self.get_attr('H', t=t)) + self.get_attr('h', t=t)
        elif attr == 'atk':
            return self.get_attr('atk0', t=t) * (1+0.01*self.get_attr('A', t=t)) + self.get_attr('a', t=t)
        elif attr == 'df':
            return self.get_attr('df0', t=t) * (1+0.01*self.get_attr('D', t=t)) + self.get_attr('d', t=t)
        elif attr == 'spd':
            return self.get_attr('spd0', t=t) * (1+0.01*self.get_attr('S', t=t)) + self.get_attr('s', t=t)
        return 0

    def get_attr_wrapper(self, attr, t=-1):
        if attr in ['hp', 'atk', 'df', 'spd']:
            return self.get_attr_complex(attr, t=t)
        return self.get_attr(attr, t=t)

    def print(self, params=SangonomiyaArchive.genshin_panel):
        print('--- attributes ---')
        for attr in params:
            value = self.get_attr_wrapper(attr)
            if value != 0:
                print('[{}: {:.1f}]'.format(SangonomiyaArchive.attr_name.get(attr, attr), value))
    
    def print_all(self, params=SangonomiyaArchive.genshin_panel):
        self.print(params)
        print('--- detailed information ---')
        for attr in self.ls:
            value = self.get_attr_wrapper(attr)
            if value != 0:
                for i, item in enumerate(self.ls[attr]):
                    if i == 0:
                        print('[{}] {}'.format(SangonomiyaArchive.attr_name.get(attr, attr), item))
                    else:
                        print('  {}'.format(item))



