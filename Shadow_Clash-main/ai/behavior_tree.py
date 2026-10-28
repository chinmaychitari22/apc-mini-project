"""SHADOW CLASH - Modular Behavior Tree Framework for Game AI.

Provides standard composable Selector, Sequence, Condition, and Action nodes.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Any


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class BehaviorNode(ABC):
    """Abstract Behavior Tree Node."""
    @abstractmethod
    def tick(self, context: Any) -> NodeStatus:
        pass


class Selector(BehaviorNode):
    """Fallback composite: succeeds if any child succeeds."""
    def __init__(self, children: list[BehaviorNode]) -> None:
        self.children = children

    def tick(self, context: Any) -> NodeStatus:
        for child in self.children:
            status = child.tick(context)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


class Sequence(BehaviorNode):
    """Sequence composite: succeeds only if all children succeed."""
    def __init__(self, children: list[BehaviorNode]) -> None:
        self.children = children

    def tick(self, context: Any) -> NodeStatus:
        for child in self.children:
            status = child.tick(context)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class Condition(BehaviorNode):
    """Leaf node that checks a predicate."""
    def __init__(self, predicate: Callable[[Any], bool]) -> None:
        self.predicate = predicate

    def tick(self, context: Any) -> NodeStatus:
        return NodeStatus.SUCCESS if self.predicate(context) else NodeStatus.FAILURE


class Action(BehaviorNode):
    """Leaf node that executes an AI behavior."""
    def __init__(self, action_func: Callable[[Any], NodeStatus]) -> None:
        self.action_func = action_func

    def tick(self, context: Any) -> NodeStatus:
        return self.action_func(context)
