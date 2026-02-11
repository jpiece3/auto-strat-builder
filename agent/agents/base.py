"""Base agent with LLM reasoning and skill access."""

from __future__ import annotations

import abc
import time
from datetime import datetime
from typing import Any

from agent.config import AgentConfig
from agent.models import TaskResult, TaskStatus, WorkflowState
from agent.utils.llm import LLMClient
from agent.utils.logging import get_logger, log_agent_step


class BaseAgent(abc.ABC):
    """Abstract base class for all intelligence-gathering agents.

    Each agent:
    - Has a specific mission (brand discovery, SEO analysis, etc.)
    - Has access to a subset of skills
    - Uses an LLM for reasoning and synthesis
    - Operates on shared WorkflowState
    - Reports results as TaskResult
    """

    name: str = "base"
    description: str = ""

    def __init__(self, config: AgentConfig, skills: dict[str, Any]) -> None:
        self.config = config
        self.skills = skills
        self.llm = LLMClient(config.llm)
        self.logger = get_logger(f"agent.{self.name}")

    @abc.abstractmethod
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute the agent's mission and update workflow state."""
        ...

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Wrapped execution with timing, error handling, and result recording."""
        log_agent_step(self.logger, self.name, "STARTING", self.description)
        started = datetime.utcnow()
        start_time = time.monotonic()

        try:
            state = await self.run(state)
            duration = time.monotonic() - start_time
            result = TaskResult(
                task_name=self.name,
                status=TaskStatus.COMPLETED,
                duration_seconds=round(duration, 2),
                started_at=started.isoformat(),
                completed_at=datetime.utcnow().isoformat(),
            )
            log_agent_step(self.logger, self.name, "COMPLETED", f"{duration:.1f}s")
        except Exception as exc:
            duration = time.monotonic() - start_time
            result = TaskResult(
                task_name=self.name,
                status=TaskStatus.FAILED,
                error=str(exc),
                duration_seconds=round(duration, 2),
                started_at=started.isoformat(),
                completed_at=datetime.utcnow().isoformat(),
            )
            log_agent_step(self.logger, self.name, "FAILED", str(exc))

        state.record_task(result)
        return state

    async def synthesize(self, system_prompt: str, data: str, question: str) -> str:
        """Use the LLM to reason about collected data."""
        prompt = f"""Based on the following data:\n\n{data}\n\n{question}"""
        return await self.llm.complete(system_prompt, prompt)

    async def extract_structured(self, system_prompt: str, data: str, question: str) -> Any:
        """Use the LLM to extract structured JSON from collected data."""
        prompt = f"""Based on the following data:\n\n{data}\n\n{question}"""
        return await self.llm.extract_json(system_prompt, prompt)
