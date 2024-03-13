import numpy as np

class Intensify:
    def __init__(self):
        self.level_base = 1446.85
        self.aggravate_mult = 1.15
        self.spread_mult = 1.25

    def em_mult(self, em):
        return (5*em) / (em+1200)

    def aggravate(self, em, extra=0):
        return self.level_base * self.aggravate_mult * (1+self.em_mult(em)+extra)

    def spread(self, em, extra=0):
        return self.level_base * self.spread_mult * (1+self.em_mult(em)+extra)

class Fusion:
    def __init__(self):
        self.level_base = 1446.85
        self.hyperconduct_mult = 0.5
        self.swirl_mult = 0.6
        self.electrocharge_mult = 1.2
        self.overload_mult = 2.0
        self.bloom_mult = 2.0
        self.hyperbloom_mult = 3.0
        self.burn_mult = 0.25

    def em_mult(self, em):
        return (16*em) / (em+2000)

    def hyperbloom(self, em, extra=0):
        return self.level_base * self.hyperbloom_mult * (1+self.em_mult(em)+extra)
    
    def bloom(self, em, extra=0):
        return self.level_base * self.bloom_mult * (1+self.em_mult(em)+extra)

class Amplify:
    def __init__(self):
        self.base = 1.5
        self.reverse_base = 2

    def em_mult(self, em):
        return (2.78*em) / (em+1400)

    def amplify(self, em):
        return self.base * (1+self.em_mult(em))

    def reverse_amplify(self, em):
        return self.reverse_base * (1+self.em_mult(em))


intensify = Intensify()
fusion = Fusion()
amplify = Amplify()

    