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

from spawn.parsers import SpecificationParser, DictSpecificationProvider
from spawn.specification import DictSpecificationConverter
from spawn.parsers.specification_parser import DEFAULT_COMBINATORS, ZIP

SPEC_1 = {
    'base_file': './file/input.in',
    'creation_time': '2018-10-19T12:00:00',
    'notes': 'Some notes',
    'spec': {
        'policy:path': 'X{alpha}/Y{beta}',
        'alpha': 12.0,
        'beta': 180.0
    }
}

EXPECTED_1 = {
    'base_file': './file/input.in',
    'metadata': {
        'creation_time': '2018-10-19T12:00:00',
        'notes': 'Some notes'
    },
    'spec': [{
        'name': 'alpha',
        'value': 12.0,
        'children': [
            {
                'path': 'X12.0/Y180.0',
                'name': 'beta',
                'value': 180.0
            }
        ]
    }]
}

SPEC_2 = {
    'base_file': './file/input.in',
    'creation_time': '2018-10-19T12:00:00',
    'notes': 'Some notes',
    'spec': {
        'policy:path': 'X{alpha}/Y{beta}',
        'alpha': 12.0,
        'beta': [0.0, 180.0]
    }
}

EXPECTED_2 = {
    'base_file': './file/input.in',
    'metadata': {
        'creation_time': '2018-10-19T12:00:00',
        'notes': 'Some notes'
    },
    'spec': [{
        'name': 'alpha',
        'value': 12.0,
        'children': [
            {
                'path': 'X12.0/Y0.0',
                'name': 'beta',
                'value': 0.0
            },
            {
                'path': 'X12.0/Y180.0',
                'name': 'beta',
                'value': 180.0
            }
        ]
    }]
}

SPEC_3 = {
    'base_file': './file/input.in',
    'creation_time': '2018-10-19T12:00:00',
    'notes': 'Some notes',
    'spec': {
        'policy:path': 'X{alpha}/Y{beta}',
        'alpha': [3.0, 12.0],
        'beta': [0.0, 180.0]
    }
}

EXPECTED_3 = {
    'base_file': './file/input.in',
    'metadata': {
        'creation_time': '2018-10-19T12:00:00',
        'notes': 'Some notes'
    },
    'spec': [{
        'name': 'alpha',
        'value': 3.0,
        'children': [
            {
                'path': 'X3.0/Y0.0',
                'name': 'beta',
                'value': 0.0
            },
            {
                'path': 'X3.0/Y180.0',
                'name': 'beta',
                'value': 180.0
            }
        ]
    },{
        'name': 'alpha',
        'value': 12.0,
        'children': [
            {
                'path': 'X12.0/Y0.0',
                'name': 'beta',
                'value': 0.0
            },
            {
                'path': 'X12.0/Y180.0',
                'name': 'beta',
                'value': 180.0
            }
        ]
    }]
}

SPEC_4 = {
    'base_file': './file/input.in',
    'creation_time': '2018-10-19T12:00:00',
    'notes': 'Some notes',
    'spec': {
        'policy:path': 'X{alpha}/Y{beta}',
        '_casper': 1.0,
        'combine:zip': {
            'alpha': [3.0, 12.0],
            'beta': [0.0, 180.0]
        }
    }
}

EXPECTED_4 = {
    'base_file': './file/input.in',
    'metadata': {
        'creation_time': '2018-10-19T12:00:00',
        'notes': 'Some notes'
    },
    'spec': [{
        'name': 'alpha',
        'value': 3.0,
        'children': [
            {
                'path': 'X3.0/Y0.0',
                'name': 'beta',
                'value': 0.0,
                'ghosts': {'casper': 1.0}
            }
        ]
    }, {
        'name': 'alpha',
        'value': 12.0,
        'children': [
            {
                'path': 'X12.0/Y180.0',
                'name': 'beta',
                'value': 180.0,
                'ghosts': {'casper': 1.0}
            }
        ]
    }]
}

def parse(spec, plugin_loader):
    return SpecificationParser(DictSpecificationProvider(spec), plugin_loader).parse()

@pytest.fixture
def dict_converter():
    return DictSpecificationConverter()

@pytest.mark.parametrize('spec,expected', [
    (SPEC_1, EXPECTED_1),
    (SPEC_2, EXPECTED_2),
    (SPEC_3, EXPECTED_3),
    (SPEC_4, EXPECTED_4),
])
def test_dict_converter_converts_parsed_spec(dict_converter, spec, expected, plugin_loader):
    spec_model = parse(spec, plugin_loader)
    assert dict_converter.convert(spec_model) == expected
