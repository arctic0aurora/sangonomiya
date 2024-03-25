from archive import *
from chara import *
from artifact import *
from formation import *

import characters.furina
import characters.benchmark.neuvillette


class BenchmarkOption():
    def __init__(self, character, feature:Composite, attached_feature={}):
        self.avatar = character
        self.feature = feature
        self.attached = attached_feature

    def print(self, print_additional=True):
        print('sort key: {}'.format(self.feature))
        for desc, feat in self.attached.items():
            print('{}: {}'.format(desc, feat))
        if print_additional:
            additional = self.avatar.additional_feature()
            for desc, feat in additional.items():
                print('{}: {}'.format(desc, feat))
        print('')       
        self.avatar.get_panel().print()
    

class BenchmarkOptimizer():
    def __init__(self, character):
        self.avatar = CharacterBase()
        self.effective_stats = {'A': 5.0, 'cr': 3.3, 'cd': 6.6} # no need to include rcg
        self.primary_stats = {
            'h': 4780, 'a': 311,
            'A': 46.6, 'bns': 46.6, 'cd': 62.2,
        }
        if character == 'furina':
            characters.furina.Furina.fanfare_sequence = characters.furina.fanfare_simulation()
            self.avatar = characters.furina.Furina(weapon='tranquil')
            self.effective_stats = {'H': 5.0, 'cr': 3.3, 'cd': 6.6}
            self.primary_stats = {
                'h': 4780, 'a': 311,
                'rcg': 51.8, 'H': 46.6, 'cd': 62.2,
            }
        elif character == 'neuvillette':
            self.avatar = characters.benchmark.neuvillette.Neuvillette(weapon='eternalflow')
            self.effective_stats = {'H': 5.0, 'cr': 3.3, 'cd': 6.6}
            self.primary_stats = {
                'h': 4780, 'a': 311,
                'H': 46.6, 'hydro': 46.6, 'cd': 62.2,
            }
        self.artifact_list = []
        artifact_id = 0
        for primary_stat in self.primary_stats:
            self.artifact_list.append(Artifact(artifact_id, SangonomiyaArchive.genshin_slots[artifact_id], 'any', {primary_stat: self.primary_stats[primary_stat]}))
            artifact_id = artifact_id + 1
        self.options = []

    def balance_crit(self, stat_limit, cr=5, cd=50, percd=6.6):
        score = stat_limit*percd + cr*2 + cd
        cr_stats = (min(200, score/2) - cr*2) // percd # in favor of cd
        cd_stats = stat_limit - cr_stats
        return (int)(cr_stats), (int)(cd_stats)

    def optimize_benchmark(self, sort_key=SangonomiyaArchive.default_sort_key, stats_base=27, stats_incre=3, args=['recharge_thres']):
        assert (len(self.effective_stats) == 3 and 'cd' in self.effective_stats) # not finished otherwise
        options = []
        stats_all = stats_base + stats_incre * (len(self.effective_stats)-3)
        if self.avatar.requirement['set-type'] == '4pcs':           
            for s in self.avatar.requirement['set-restriction']:
                alist = copy.deepcopy(self.artifact_list)
                for item in alist:
                    item.set = s
                _art = ArtifactCollection(alist)
                _avatar = copy.deepcopy(self.avatar)               
                _avatar.apply_artifacts(_art)
                rcgn = 0
                if 'recharge_thres' in args:
                    rcgn = (int)(min(np.ceil(max(_avatar.recharge_thres-_avatar.rcg(), 0) / 5.5), stats_all-2*stats_incre))
                    stats_limit = stats_all - max(0, rcgn-stats_incre) # first 3 recharges for free
                    rcgn = max(stats_incre, rcgn)
                for crits in range(stats_limit+1):                   
                    if crits > stats_limit-stats_incre or stats_limit-crits > stats_limit-2*stats_incre:
                        continue
                    for substat in self.effective_stats:
                        if substat != 'cr' and substat != 'cd':
                            atk_equiv = substat
                    crn, cdn = self.balance_crit(crits, _avatar.cr(), _avatar.cd(), percd=self.effective_stats['cd'])
                    atkn = stats_limit - crits # or hpn, dfn
                    substats_attr = {
                        'cr': self.effective_stats['cr'] * crn,
                        'cd': self.effective_stats['cd'] * cdn,
                        atk_equiv: self.effective_stats[atk_equiv] * atkn,
                        'rcg': 5.5 * rcgn,
                    }
                    art = copy.deepcopy(_art)
                    art.append(Artifact(65535, 'any', 'any', substats_attr))
                    avatar = copy.deepcopy(self.avatar)                                
                    avatar.apply_artifacts(art)
                    optim_target, attached = avatar.optim_target()
                    option = BenchmarkOption(avatar, optim_target, attached)
                    options.append(option)
        options = sorted(options, key=sort_key, reverse=True)
        self.options = options

    def print_result(self):
        print('')
        print('---------- Benchmark Report ----------')
        print('')
        if len(self.options) < 1:
            print('No option found.')
            return
        self.options[0].print()




                
