import numpy as np


def gridify(variables):
    lists = []
    keys = []
    for key, value in variables.items():
        keys.append(key)
        lists.append(value)
    grid = np.meshgrid(*lists)
    arrays = [g.ravel() for g in grid]
    runs = []
    for i in range(len(arrays[0])):
        runs.append({keys[j]: arrays[j][i] for j in range(len(keys))})
    return runs
