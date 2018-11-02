"""Runners for :mod:`multiwindcalc` tasks

A runner has a ``run`` method, which runs the work required for a task, and a ``complete`` method, which returns ``True`` when the task has completed.
"""
from .process_runner import ProcessRunner
from .factories import RunnerFactory