"""
Mesa Time Module
================

Objects for handling simulation time.

"""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mesa.model import Model


class BaseScheduler:
    """Simplest scheduler; activates agents one at a time, in the order
    they were added.

    Assumes that each agent added has a *step* method which takes no arguments.

    (This is explicitly not meant to be realistic, but it is useful for simple
    models and for testing.)

    """

    def __init__(self, model: Model) -> None:
        """Create a new, empty BaseScheduler."""
        self.model = model
        self.steps = 0
        self.time = 0.0
        self._agents: dict[int, Any] = {}

    def add(self, agent: Any) -> None:
        """Add an Agent object to the schedule.

        Args:
            agent: An Agent to be added to the schedule. NOTE: The agent must
            have a ``unique_id`` property.

        """
        if agent.unique_id in self._agents:
            raise Exception(
                f"Agent with unique id {agent.unique_id!r} already added."
            )

        self._agents[agent.unique_id] = agent

    def remove(self, agent: Any) -> None:
        """Remove all instances of a given agent from the schedule.

        Args:
            agent: An agent object.

        """
        del self._agents[agent.unique_id]

    def step(self) -> None:
        """Execute the step of all the agents, one at a time."""
        for agent in self.agent_buffer(shuffled=False):
            agent.step()
        self.steps += 1
        self.time += 1

    def get_agent_count(self) -> int:
        """Returns the current number of agents in the queue."""
        return len(self._agents)

    @property
    def agents(self) -> list[Any]:
        """Return a list of the agents in the scheduler."""
        return list(self._agents.values())

    def agent_buffer(self, shuffled: bool = False) -> Iterator[Any]:
        """Simple generator that yields the agents while handling agent removal
        during the step.

        Args:
            shuffled: If True, yield the agents in shuffled order.

        """
        agent_keys = list(self._agents.keys())
        if shuffled:
            self.model.random.shuffle(agent_keys)

        for key in agent_keys:
            if key in self._agents:
                yield self._agents[key]


class RandomActivation(BaseScheduler):
    """A scheduler which activates each agent once per step, in random order.

    Has an agent_buffer method that is a generator yielding the agents
    in a random order.

    """

    def step(self) -> None:
        """Executes the step of all agents, one at a time, in
        random order.

        """
        for agent in self.agent_buffer(shuffled=True):
            agent.step()
        self.steps += 1
        self.time += 1


class SimultaneousActivation(BaseScheduler):
    """A scheduler to simulate the simultaneous activation of all the agents.

    This scheduler requires that each agent have two methods: step and advance.
    step() activates the agent and stages an action, and advance() enacts the
    staged action.

    """

    def step(self) -> None:
        """Executes the step of all agents, one at a time."""
        for agent in self.agent_buffer(shuffled=False):
            agent.step()
        for agent in self.agent_buffer(shuffled=False):
            agent.advance()
        self.steps += 1
        self.time += 1


class StagedActivation(BaseScheduler):
    """A scheduler which allows agent activation to be divided into several
    stages. All agents execute one stage before moving on to the next.

    Agents must have a step() method. The step() method is called on each
    agent for each stage.

    The order of agent activation within each stage is random by default.
    The stage order is fixed.

    This scheduler has one addition to the BaseScheduler:
    ``stage_list``: a list of stage names.

    Agents must have a step() method.

    TODO: Have the stage list be a list of methods to call, rather than
    strings to check for.

    """


    def __init__(
        self,
        model: Model,
        stage_list: list[str] | None = None,
        shuffle: bool = True,
        shuffle_between_stages: bool = False,
    ) -> None:
        """Create a new StagedActivation scheduler.

        Args:
            model: The model object that the scheduler belongs to.
            stage_list: A list of strings that represent the names of stages
                to proceed through.
            shuffle: If True, shuffle the order of agents within each stage.
            shuffle_between_stages: If True, shuffle the agents anew between
                each stage.

        """
        super().__init__(model)
        if stage_list is None:
            self.stage_list = []
        else:
            self.stage_list = stage_list
        self.shuffle = shuffle
        self.shuffle_between_stages = shuffle_between_stages

    def step(self) -> None:
        """Executes all the stages for all agents."""
        agent_keys = list(self._agents.keys())
        if self.shuffle:
            self.model.random.shuffle(agent_keys)
        for stage in self.stage_list:
            for agent_key in agent_keys:
                if agent_key in self._agents:  # agent may have been removed
                    getattr(self._agents[agent_key], stage)()  # Call stage method
            if self.shuffle and self.shuffle_between_stages:
                self.model.random.shuffle(agent_keys)
        self.steps += 1
        self.time += 1