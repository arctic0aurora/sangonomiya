from archive import *
from chara import *
from artifact import *
from formation import *

import copy

class Option():
    def __init__(self, character, artifacts:ArtifactCollection, team, args, feature:Composite, attached_feature={}):
        self.avatar = character
        self.artifacts = artifacts
        self.team = team
        self.args = args
        self.feature = feature
        self.attached = attached_feature

    def print(self, print_additional=True):
        print('sort key: {}'.format(self.feature))
        for desc, feat in self.attached.items():
            print('{}: {}'.format(desc, feat))
        if print_additional:
            additional = self.avatar.additional_feature(self.team, self.args)
            for desc, feat in additional.items():
                print('{}: {}'.format(desc, feat))
        print('')       
        self.avatar.get_panel().print()
        self.artifacts.print()
        

class Optimizer():
    def __init__(self, character, path, team=[], args=[]):
        self.avatar = character
        self.inv = ArtifactInventory(data_path=path)
        self.team = team
        self.args = args
        self.options = []

    def optimize_artifacts(self, requirement={}, sort_key=SangonomiyaArchive.default_sort_key):        
        set_counts = {}
        options = []
        search_space = 0
        # naive search
        for f in self.inv.artifacts['flower']:
            set_counts[f.set] = set_counts.get(f.set, 0) + 1
            for p in self.inv.artifacts['plume']:
                set_counts[p.set] = set_counts.get(p.set, 0) + 1
                if self.prune(requirement, set_counts):
                        set_counts[p.set] -= 1
                        continue
                for h in self.inv.artifacts['hourglass']:
                        set_counts[h.set] = set_counts.get(h.set, 0) + 1
                        if self.prune(requirement, set_counts):
                            set_counts[h.set] -= 1
                            continue
                        for g in self.inv.artifacts['goblet']:
                            set_counts[g.set] = set_counts.get(g.set, 0) + 1
                            if self.prune(requirement, set_counts):
                                set_counts[g.set] -= 1
                                continue
                            for c in self.inv.artifacts['circlet']:
                                set_counts[c.set] = set_counts.get(c.set, 0) + 1
                                if self.prune(requirement, set_counts):
                                    set_counts[c.set] -= 1
                                    continue
                                # calculate optimization target
                                search_space += 1
                                avatar = copy.deepcopy(self.avatar)
                                art = ArtifactCollection([f,p,h,g,c])
                                avatar.apply_artifacts(art)
                                optim_target, attached = avatar.optim_target(team=self.team, args=self.args)
                                option = Option(avatar, art, self.team, self.args, optim_target, attached)
                                options.append(option)
                                set_counts[c.set] -= 1
                            set_counts[g.set] -= 1
                        set_counts[h.set] -= 1
                set_counts[p.set] -= 1
            set_counts[f.set] -= 1
        options = sorted(options, key=sort_key, reverse=True)
        self.options = options

    # cut branch that is impossible to meet requirement
    def prune(self, req, cnts:dict, capacity=5) -> bool:
        if req['set-type'] == 'none':
            return False
        n = sum(cnts.values())
        if req['set-type'] == '4pcs':
            prime = max(cnts, key=lambda k:cnts[k]) # find the max key-value in dict
            prime_cnt = cnts[prime]
            if prime_cnt < n-(capacity-4):
                return True         
            if prime_cnt > capacity-4 and not prime in req['set-restriction']:
                return True               
        elif req['set-type'] == '2+2pcs':
            assert len(req['set-restriction']) > 1
            if n > capacity-4:
                remaining = {}
                for s in req['set-restriction']:
                        remaining[s] = max(0, 2-cnts.get(s, 0))
                rem_cnts = sorted(remaining.values())
                if rem_cnts[0]+rem_cnts[1] > capacity-n:
                        return True
        return False
        

    def print_options(self, counts=10):
        print('')
        print('---------- Optimization Report ----------')
        print('# options beyond threshold = {}'.format(len(self.options)))
        for i in range(counts):
            if i >= len(self.options):
                break
            print('')
            print('#{} option --------------------'.format(i+1))
            self.options[i].print()


