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
from spawn.parsers.generators import GeneratorsParser


def test_can_instantiate_simple_generator():
    gens = GeneratorsParser.default().parse({'Gen1': {'method': 'RandomInt'}})
    assert 'Gen1' in gens
    assert isinstance(gens['Gen1'].evaluate(), int)


def test_passes_args_correctly():
    gen_spec = {'Gen1': {
        'method': 'IncrementalInt',
        'start': 50,
        'step': 2
    }}
    gens = GeneratorsParser.default().parse(gen_spec)
    assert gens['Gen1'].evaluate() == 50
    assert gens['Gen1'].evaluate() == 52


def test_invokes_scipy_uniform_correctly():
    gen_spec = {'Gen1': {
        'method': 'scipy.uniform',
        'loc': 3.0,
        'scale': 0.1
    }}
    gens = GeneratorsParser.default().parse(gen_spec)
    assert 3.0 <= gens['Gen1'].evaluate() <= 3.1


def test_raises_key_error_when_method_not_present():
    with pytest.raises(KeyError):
        GeneratorsParser.default().parse({'Gen1': {'key': 'val'}})


def test_raises_key_error_when_method_not_class_in_generator_methods():
    with pytest.raises(KeyError):
        GeneratorsParser.default().parse({'Gen1': {'method': 'list'}})
