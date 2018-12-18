# multiwindcalc
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
from os import path
folder = path.dirname(path.realpath(__file__))
turbsim_exe = path.join(folder, 'TurbSim.exe')
fast_exe = path.join(folder, 'FASTv7.0.2.exe')
turbsim_input_file = path.join(folder, 'fast_input_files', 'TurbSim.inp')
fast_input_file = path.join(folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst')