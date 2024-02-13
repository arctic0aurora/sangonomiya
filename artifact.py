from archive import *

import numpy as np
import copy

class Artifact():
    def __init__(self, uid, slot='flower', set='troupe', attrs={}):
        self.uid = uid
        self.slot = slot
        self.set = set
        self.attrs = attrs

    def print(self):
        print(self.uid)
        print('{} of set {}'.format(self.slot, self.set))
        for key, value in self.attrs.items():
            if key in attribute_names:
                print('{}: {:.1f}'.format(attribute_names[key], value))


class ArtifactCollection():
    def __init__(self, artifact_list):
        self.alist = artifact_list
        self.set_counts = self.count_sets()
        # self.attrs = self.calculate_attrs()

    def append(self, artifact:Artifact):
        self.alist.append(artifact)
        self.set_counts[artifact.set] = self.set_counts.get(artifact.set, 0) + 1

    def contains(self, set, num):
        return (set in self.set_counts and self.set_counts[set] >= num)

    def count_sets(self):
        sets = {}
        for artifact in self.alist:
            sets[artifact.set] = sets.get(artifact.set, 0) + 1
        return sets

    def calculate_attrs(self):
        attrs = {}
        for artifact in self.alist:
            for key in artifact.attrs:
                attrs[key] = attrs.get(key, 0) + artifact.attrs[key]
        return attrs
    
    def print(self):
        print('Artifacts:')
        for artifact_set, count in self.set_counts.items():
            print('{}: {}'.format(artifact_set, count))
        for artifact in self.alist:
            print('')
            artifact.print()


class ArtifactInventory():
    def __init__(self, slots=genshin_slots, data_path='./artefacts/general'):
        self.id = 0
        self.path = data_path
        self.artifacts = {}
        for slot in slots:
            self.artifacts[slot] = []
        self.read_artifacts()
    
    def read_artifacts_from_file(self, file_path, slot):
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    if line.isalpha():
                        cur_item = Artifact(self.id, slot, line, attrs={})
                        self.artifacts[slot].append(cur_item)
                        self.id += 1
                    else:
                        key, value = line.split(' = ')
                        self.artifacts[slot][-1].attrs[key] = float(value)

    def read_artifacts(self):
        for slot in self.artifacts:
            file_path = self.path + './{}.txt'.format(slot)
            self.read_artifacts_from_file(file_path, slot)



if __name__ == '__main__':
    inv = ArtifactInventory()
    print(inv.artifacts)