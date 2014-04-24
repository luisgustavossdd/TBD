'''
Created on Apr 22, 2014

@author: LuisGustavo
'''

from itertools import combinations

def probability(subset, set):
    if not isinstance(subset,list): subset = [subset]
    subset_size = len(subset)
    possible_subsets = [list(s) for s in combinations(set,subset_size)]
    return float(possible_subsets.count(subset))/len(possible_subsets)

