"""Schedulers for ``multiwindcalc``

A scheduler understands how to turn a spec into a list of jobs and related dependncies to run
"""
from .luigi import LuigiScheduler
