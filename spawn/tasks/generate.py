# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
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
"""Methods to generate :class:`SimulationTask`s
"""
from spawn.util import PathBuilder, TypedProperty
from spawn.specification.specification import SpecificationNode, IndexedNode

def _check_type(task_spawner, name, value):
    if hasattr(type(task_spawner), name):
        attribute = getattr(type(task_spawner), name)
        if isinstance(attribute, TypedProperty):
            expected_type = attribute.type
            if not isinstance(value, expected_type):
                value = expected_type(value)
    return value

def generate_tasks_from_spec(task_spawner, node, base_path):
    """Generate list of luigi.Task for a spawn.SpecificationNode"""
    if not isinstance(node, SpecificationNode):
        raise ValueError('node must be of type ' + SpecificationNode.__name__)
    if node.has_property:
        value = _check_type(task_spawner, node.property_name, node.property_value)
        if isinstance(node, IndexedNode):
            array = getattr(task_spawner, node.property_name)
            array[node.index] = value
        else:
            setattr(task_spawner, node.property_name, value)
    if not node.children:   # (leaf)
        task = task_spawner.spawn(
            str(PathBuilder(base_path).join(node.path)),
            {**node.ghosts, **node.collected_properties}
        )
        return [task]
    # (branch)
    tasks = []
    for child in node.children:
        branch = task_spawner.branch()
        tasks += generate_tasks_from_spec(branch, child, base_path)
    return tasks
