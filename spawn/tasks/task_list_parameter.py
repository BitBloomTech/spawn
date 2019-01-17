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
"""Defines the :class:`TaskListParameter` to provide numerous tasks as
dependencies for `luigi`
"""
from collections.abc import Mapping
import json
import luigi

class _TaskEncoder(json.JSONEncoder):
    #pylint: disable=E0202
    def default(self, o):
        if isinstance(o, Mapping):
            return dict(o.items())
        return super().default(o)

class TaskListParameter(luigi.Parameter):
    """Implementation of :class:`luigi.Parameter` to allow definitions of
    multiple tasks as dependencies
    """
    def parse(self, x):
        """Parse the string
        """
        input_dicts = json.loads(x)
        return [
            luigi.task_register.Register.get_task_cls(i['family'])(**i['params'])
            for i in input_dicts
        ]

    def serialize(self, x):
        """Serialize this object
        """
        tasks = []
        for obj in x:
            if not isinstance(obj, luigi.Task):
                continue
            task = {
                'family': obj.get_task_family(),
                'params': {}
            }
            for param_name, _param_obj in obj.get_params():
                if hasattr(obj, param_name):
                    task['params'][param_name] = getattr(obj, param_name)
            tasks.append(task)
        return json.dumps(tasks, cls=_TaskEncoder)
