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
import inspect

from spawn.util.validation import validate_type

class ValueProxy:
    def evaluate(self):
        return NotImplementedError()


class Macro(ValueProxy):
    def __init__(self, value):
        self._value = value

    def evaluate(self):
        return self._value

def evaluate(value_proxy, *args, **kwargs):
    validate_type(value_proxy, ValueProxy, 'value_proxy')
    parameters = inspect.signature(value_proxy.evaluate).parameters
    if 'kwargs' in parameters:
        return value_proxy.evaluate(*args, **kwargs)
    else:
        return value_proxy.evaluate(*args)
