from app.services.interview_context.schemas.interview_context import InterviewContext
from app.services.interview_planner.schemas.interview_plan import InterviewPlan
from app.services.interview_planner.schemas.interview_phase import InterviewPhase
from app.services.interview_planner.schemas.interview_objective import InterviewObjective

class InterviewPlanner:
    """
    Stateless, deterministic service that transforms an InterviewContext 
    into an InterviewPlan.
    """
    
    @classmethod
    def build(cls, context: InterviewContext) -> InterviewPlan:
        phases = []
        
        # Phase 1: Introduction
        intro_phase = InterviewPhase(
            name="Introduction",
            description="Ice breaker and candidate introduction.",
            ordering=1,
            allocated_minutes=1,
            objectives=[
                InterviewObjective(
                    name="Communication",
                    description="Evaluate communication skills.",
                    priority=10
                )
            ]
        )
        phases.append(intro_phase)
        
        # Phase 2: Projects
        project_objectives = []
        for project in context.candidate.projects:
            project_objectives.append(
                InterviewObjective(
                    name=project.name,
                    description=f"Discuss project: {project.name}",
                    priority=9
                )
            )
        project_phase = InterviewPhase(
            name="Projects",
            description="Discuss candidate projects.",
            ordering=2,
            allocated_minutes=1,
            objectives=project_objectives
        )
        phases.append(project_phase)
        
        # Phase 3: Technical
        tech_objectives = []
        for skill in context.job.requirements.required_skills:
            tech_objectives.append(
                InterviewObjective(
                    name=skill.name,
                    description=f"Evaluate {skill.name}.",
                    priority=10
                )
            )
        tech_phase = InterviewPhase(
            name="Technical",
            description="Evaluate technical skills.",
            ordering=3,
            allocated_minutes=1,
            objectives=tech_objectives
        )
        phases.append(tech_phase)
        
        # Phase 4: Behavioral
        behavioral_phase = InterviewPhase(
            name="Behavioral",
            description="Behavioral assessment.",
            ordering=4,
            allocated_minutes=1,
            objectives=[
                InterviewObjective(
                    name="Problem Solving",
                    description="Behavioral questions.",
                    priority=8
                )
            ]
        )
        phases.append(behavioral_phase)
        
        # Phase 5: Closing
        closing_phase = InterviewPhase(
            name="Closing",
            description="Wrap up interview.",
            ordering=5,
            allocated_minutes=1,
            objectives=[]
        )
        phases.append(closing_phase)
        
        allocated_phases = cls._allocate_time(phases, context.configuration.duration_minutes)
        
        return InterviewPlan(
            phases=allocated_phases,
            total_duration_minutes=context.configuration.duration_minutes,
            role=context.configuration.role,
            experience_level=context.configuration.experience_level
        )

    @classmethod
    def _allocate_time(cls, phases: list[InterviewPhase], total_minutes: int) -> list[InterviewPhase]:
        """
        Allocate interview time across phases based on deterministic weights.
        Returns a new list of InterviewPhases to preserve immutability.
        """
        weights = {
            "Introduction": 0.10,
            "Projects": 0.25,
            "Technical": 0.45,
            "Behavioral": 0.15,
            "Closing": 0.05,
        }
        
        remaining = total_minutes
        allocated_phases = []
        
        for i, phase in enumerate(phases):
            if i == len(phases) - 1:
                minutes = max(remaining, 1)
            else:
                minutes = max(1, round(total_minutes * weights.get(phase.name, 0.0)))
            
            allocated_phases.append(
                InterviewPhase(
                    name=phase.name,
                    description=phase.description,
                    ordering=phase.ordering,
                    allocated_minutes=minutes,
                    objectives=phase.objectives
                )
            )
            remaining -= minutes
            
        return allocated_phases
