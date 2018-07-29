from multiwindcalc.run_generator.combinators import gridify


def test_gridify_creates_2d_grid():
    seeds = [1, 4, 6]
    numbers = [5, 2, -3, 9]
    runs = gridify({'seed': seeds, 'number': numbers})
    assert(len(runs) == len(seeds)*len(numbers))
    for s in seeds:
        for n in numbers:
            assert({'seed': s, 'number': n} in runs)


def test_gridify_creates_3d_grid():
    apples = [1, 3]
    pears = [-1, -3, 4]
    oranges = [20, 21, 14, 16]
    runs = gridify({'apple': apples, 'pear': pears, 'orange': oranges})
    assert(len(runs) == len(apples)*len(pears)*len(oranges))
    for a in apples:
        for p in pears:
            for o in oranges:
                assert({'apple': a, 'pear': p, 'orange': o} in runs)


def test_gridify_can_combine_different_types():
    doubles = [3.4, 6.5]
    strings = ['hello', 'world']
    runs = gridify({'doubles': doubles, 'strings': strings})
    for run in runs:
        assert(isinstance(run['doubles'], float))
        assert(isinstance(run['strings'], str))

