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
"""Base task for all Spawn tasks
"""
import luigi

from .task_list_parameter import TaskListParameter


class SpawnTask(luigi.Task):
    """Implementation of :class:`luigi.Task` that defines ID and dependencies parameters
    """
    _id = luigi.Parameter()
    _metadata = luigi.DictParameter(default={})
    _dependencies = TaskListParameter(default=[])

    def run(self):
        """Run the task. Derived classes should implement this method.
        """
        raise NotImplementedError()

    def complete(self):
        """Determine if this task is complete

        :returns: ``True`` if this task is complete; otherwise ``False``
        :rtype: bool
        """
        raise NotImplementedError()

    def requires(self):
        """The prerequisites for this task
        """
        return self._dependencies

    @property
    def metadata(self):
        """Metadata for this task
        """
        return self._metadata
