"""
==============================================================================
Interview Phase

Purpose:
Represents one logical phase of an interview.

Example:

Technical Phase

Objectives:
- Python
- FastAPI
- Docker

Time Budget:
20 minutes

The Interview Planner creates phases.

The Interview Orchestrator moves through them during the interview.

This is a runtime domain model.
==============================================================================
"""

from pydantic import BaseModel, Field

from app.schemas.interview_engine.interview_objective import (
    InterviewObjective,
)


class InterviewPhase(BaseModel):
    """
    One interview phase.
    """

    name: str = Field(
        description="Phase name."
    )

    description: str = Field(
        description="Purpose of this phase."
    )

    allocated_minutes: int = Field(
        gt=0,
        description="Planned duration."
    )

    objectives: list[InterviewObjective] = Field(
        default_factory=list
    )

    completed: bool = False