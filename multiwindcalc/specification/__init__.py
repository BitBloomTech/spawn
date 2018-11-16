"""Specification definition

The :class:`SpecificationModel` contains the definition of the tasks to be spawned
"""
from .specification import SpecificationModel, SpecificationMetadata, SpecificationNode, ValueProxyNode, SpecificationNodeFactory
from .converters import DictSpecificationConverter
from .value_proxy import ValueProxy, Macro, evaluate
from .evaluators import Evaluator
