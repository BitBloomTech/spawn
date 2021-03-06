# spawn
# Copyright (C) 2018, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
import pytest
from spawn.specification.generator_methods import *


def test_random_int_always_in_range():
    r = RandomInt(min=10, max=20)
    for i in range(20):
        v = r.evaluate()
        assert 10 <= v <= 20


def test_two_random_generators_give_same_results():
    r1 = RandomInt()
    r2 = RandomInt()
    for i in range(20):
        assert r1.evaluate() == r2.evaluate()


def test_random_generators_with_different_seeds_give_different_values():
    r1 = RandomInt(seed=1)
    r2 = RandomInt(seed=2)
    assert r1.evaluate() != r2.evaluate()


def test_incremental_int():
    gen = IncrementalInt(start=10, step=5)
    assert gen.evaluate() == 10
    assert gen.evaluate() == 15
    assert gen.evaluate() == 20


def test_scipy_uniform():
    gen = ScipyDistribution('uniform', loc=5.0, scale=0.1)
    assert 5.0 <= gen.evaluate() <= 5.1


def test_same_random_state_gives_same_value():
    gen1 = ScipyDistribution('norm', random_state=2, scale=2.0)
    gen2 = ScipyDistribution('norm', random_state=2, scale=2.0)
    assert gen1.evaluate() == gen2.evaluate()


def test_raises_value_error_with_invalid_scipy_distribution():
    with pytest.raises(KeyError):
        ScipyDistribution('not_a_scipy_distribution')
