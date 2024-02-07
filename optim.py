from archive import *
from chara import *
from artifact import *
from formation import *

import copy

class Option():
     def __init__(self, character, artifacts:ArtifactCollection, feature:Composite, attached_feature={}):
          self.avatar = character
          self.artifacts = artifacts
          self.feature = feature
          self.attached = attached_feature

     def print(self, print_attached=True):
          print('sort key: {}'.format(self.feature))
          for desc, feat in self.attached.items():
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
          
     def optimize_artifacts(self, prune_cond={}, sort_key=default_sort_key):
          options = []
          search_space = 0
          # naive search
          for f in self.inv.artifacts['flower']:
               for p in self.inv.artifacts['plume']:
                    if prune_check([f,p], prune_cond):
                         continue
                    for h in self.inv.artifacts['hourglass']:
                         if prune_check([f,p,h], prune_cond):
                              continue
                         for g in self.inv.artifacts['goblet']:
                              if prune_check([f,p,h,g], prune_cond):
                                   continue
                              for c in self.inv.artifacts['circlet']:
                                   if prune_check([f,p,h,g,c], prune_cond):
                                        continue
                                   # calculate optimization target
                                   search_space += 1
                                   avatar = copy.deepcopy(self.avatar)
                                   art = ArtifactCollection([f,p,h,g,c])
                                   avatar.apply_artifacts(art)
                                   optim_target, attached = avatar.optim_target(team=self.team, args=self.args)
                                   if 'thres' in prune_cond and optim_target.exp > prune_cond['thres']:
                                        option = Option(avatar, art, optim_target, attached)
                                        options.append(option)
          options = sorted(options, key=sort_key, reverse=True)
          self.options = options

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


