import pytest

import io
from os import path
from glob import glob
import json

import numpy as np

import spawn
from spawn.config import DefaultConfiguration

@pytest.fixture
def spec():
    with open('example_data/example_spec.json') as fp:
        return json.load(fp)

def test_tasks_are_run_via_interface(tmpdir):
    config = DefaultConfiguration()
    config.set_default('plugins', 'test:tests.conftest')
    config.set_default('type', 'test')
    config.set_default('outdir', tmpdir)
    config.set_default('workers', 1)
    config.set_default('local', True)
    spec_dict = {'spec': {'alpha': list(np.arange(4.0, 10.0, 2.0))}}
    spawn.run(spec_dict, config)
    assert path.isfile(path.join(str(tmpdir), 'spawn.json'))
    assert len(glob(str(tmpdir) + '/**')) == 7

def test_can_get_stats(spec):
    stats = spawn.stats(spec)
    assert 'leaf_count' in stats
    assert stats['leaf_count'] > 0

def test_can_inspect(spec):
    result = spawn.inspect(spec)
    assert isinstance(result, dict)
    assert 'spec' in result
    assert result['spec']

def test_can_write_inspection(tmpdir, spec):
    result = spawn.inspect(spec)
    filepath = path.join(tmpdir, 'inspection.json')
    spawn.write_inspection(result, out=filepath, format='json')
    with open(filepath) as fp:
        assert json.load(fp) == result
    
def test_can_write_inspection_to_stream(tmpdir, spec):
    result = spawn.inspect(spec)
    filepath = path.join(tmpdir, 'inspection.json')
    stream = io.StringIO()
    spawn.write_inspection(result, out=stream, format='json')
    stream.seek(0)
    assert json.load(stream) == result
