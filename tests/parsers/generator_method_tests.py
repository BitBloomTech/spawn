from multiwindcalc.specification.generator_methods import *


def test_random_int_always_in_range():
    r = RandomInt(min=10, max=20)
    for i in range(20):
        v = r.generate()
        assert 10 <= v <= 20


def test_two_random_generators_give_same_results():
    r1 = RandomInt()
    r2 = RandomInt()
    for i in range(20):
        assert r1.generate() == r2.generate()


def test_random_generators_with_different_seeds_give_different_values():
    r1 = RandomInt(seed=1)
    r2 = RandomInt(seed=2)
    assert r1.generate() != r2.generate()


def test_incremental_int():
    gen = IncrementalInt(start=10, step=5)
    assert gen.generate() == 10
    assert gen.generate() == 15
    assert gen.generate() == 20
