"""
MultiWindCalc root module
=================================================

.. :platform: Unix, Windows
   :synopsis: Concisely declare and run simulations with many parameter permutations.
.. moduleauthor:: Michael Tinning <michael.tinning@simmovation.tech>
.. moduleauthor:: Philip Bradstock <philip.bradstock@simmovation.tech>
"""
from . import spawners, simulation_inputs, tasks, generate_tasks
from .parsers import SpecificationFileReader, SpecificationParser
