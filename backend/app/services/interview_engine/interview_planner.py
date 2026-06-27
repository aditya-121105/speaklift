"""
==============================================================================
Interview Planner

Purpose:
Generate a complete InterviewPlan from an InterviewContext.

Responsibilities

✔ Decide interview phases
✔ Allocate interview time
✔ Generate interview objectives

Does NOT

✘ Generate questions
✘ Evaluate answers
✘ Call LLMs

The planner is deterministic.

Later versions may use AI to optimize planning,
but the public interface will remain unchanged.
==============================================================================
"""

from app.schemas.interview_engine.interview_context import (
    InterviewContext,
)

from app.schemas.interview_engine.interview_objective import (
    InterviewObjective,
)

from app.schemas.interview_engine.interview_phase import (
    InterviewPhase,
)

from app.schemas.interview_engine.interview_plan import (
    InterviewPlan,
)


class InterviewPlanner:
    """
    Generate an interview execution plan.
    """

    @classmethod
    def build(
        cls,
        context: InterviewContext,
    ) -> InterviewPlan:

        phases = [
            cls._build_introduction_phase(),
            cls._build_project_phase(context),
            cls._build_technical_phase(context),
            cls._build_behavioral_phase(),
            cls._build_closing_phase(),
        ]

        cls._allocate_time(
            phases,
            context.duration_minutes,
        )

        return InterviewPlan(
            phases=phases,
            total_duration_minutes=(
                context.duration_minutes
            ),
        )

    @staticmethod
    def _build_introduction_phase() -> InterviewPhase:

        return InterviewPhase(
            name="Introduction",
            description="Ice breaker and candidate introduction.",
            allocated_minutes=1,
            objectives=[
                InterviewObjective(
                    name="Communication",
                    description="Evaluate communication skills.",
                    priority=10,
                )
            ],
        )

    @staticmethod
    def _build_project_phase(
        context: InterviewContext,
    ) -> InterviewPhase:

        objectives = [
            InterviewObjective(
                name=project,
                description=f"Discuss project: {project}",
                priority=9,
            )
            for project in context.candidate_profile.projects
        ]

        return InterviewPhase(
            name="Projects",
            description="Discuss candidate projects.",
            allocated_minutes=1,
            objectives=objectives,
        )

    @staticmethod
    def _build_technical_phase(
        context: InterviewContext,
    ) -> InterviewPhase:

        objectives = [
            InterviewObjective(
                name=skill,
                description=f"Evaluate {skill}.",
                priority=10,
            )
            for skill in context.job_profile.required_skills
        ]

        return InterviewPhase(
            name="Technical",
            description="Evaluate technical skills.",
            allocated_minutes=1,
            objectives=objectives,
        )

    @staticmethod
    def _build_behavioral_phase() -> InterviewPhase:

        return InterviewPhase(
            name="Behavioral",
            description="Behavioral assessment.",
            allocated_minutes=1,
            objectives=[
                InterviewObjective(
                    name="Problem Solving",
                    description="Behavioral questions.",
                    priority=8,
                )
            ],
        )

    @staticmethod
    def _build_closing_phase() -> InterviewPhase:

        return InterviewPhase(
            name="Closing",
            description="Wrap up interview.",
            allocated_minutes=1,
            objectives=[],
        )

    @staticmethod
    def _allocate_time(
        phases: list[InterviewPhase],
        total_minutes: int,
    ) -> None:
        """
        Allocate interview time.

        Current version distributes time proportionally.

        Future versions may use AI optimization.
        """

        weights = {
            "Introduction": 0.10,
            "Projects": 0.25,
            "Technical": 0.45,
            "Behavioral": 0.15,
            "Closing": 0.05,
        }

        remaining = total_minutes

        for phase in phases[:-1]:
            minutes = max(
                1,
                round(
                    total_minutes *
                    weights[phase.name]
                ),
            )

            phase.allocated_minutes = minutes
            remaining -= minutes

        phases[-1].allocated_minutes = max(
            remaining,
            1,
        )