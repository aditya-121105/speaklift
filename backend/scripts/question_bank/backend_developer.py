# backend/scripts/question_bank/backend_developer.py
"""
Backend Developer question collection.

30 production-quality interview questions for the Backend Developer role.
Experience level: FRESHER (entry-level, up to ~1 year experience).

Topics covered:
  Python · OOP · FastAPI · REST APIs · SQL · PostgreSQL · SQLAlchemy
  Authentication · JWT · Docker · Git · Linux · HTTP · API Design
  Error Handling · Performance · Caching · Async Programming · Testing
  System Design (junior level)

Category distribution:
  INTRODUCTION   — 4 questions
  PROJECT        — 5 questions
  TECHNICAL      — 13 questions
  ROLE_SPECIFIC  — 5 questions
  BEHAVIORAL     — 3 questions

Difficulty distribution:
  EASY   — 10 questions
  MEDIUM — 13 questions
  HARD   —  7 questions

Expose: QUESTIONS (list[QuestionBank])
"""

from app.models.question_bank import QuestionBank
from app.shared.enums import DifficultyLevel, ExperienceLevel, QuestionCategory

from .common import create_question

_ROLE = "Backend Developer"
_LEVEL = ExperienceLevel.FRESHER

QUESTIONS: list[QuestionBank] = [

    # =========================================================================
    # INTRODUCTION  (4 questions)
    # =========================================================================

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "Tell me about yourself and what drew you to backend development."
        ),
        skills=["Communication", "Self-awareness"],
        technologies=[],
        expected_concepts=[
            "Clear Narrative",
            "Technical Interest",
            "Relevant Background",
            "Career Direction",
        ],
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "Walk me through the backend technologies you are most comfortable "
            "with and explain why you chose to learn them."
        ),
        skills=["Backend Development", "Technology Selection"],
        technologies=["Python", "FastAPI", "PostgreSQL"],
        expected_concepts=[
            "Technology Rationale",
            "Practical Experience",
            "Learning Approach",
            "Ecosystem Awareness",
        ],
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What does a typical day look like when you are working on a "
            "personal or academic backend project?"
        ),
        skills=["Software Development", "Work Habits"],
        technologies=[],
        expected_concepts=[
            "Development Workflow",
            "Version Control",
            "Iterative Development",
            "Problem Solving",
        ],
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Describe the most technically challenging backend problem you have "
            "encountered so far and how you resolved it."
        ),
        skills=["Problem Solving", "Backend Development", "Debugging"],
        technologies=["Python"],
        expected_concepts=[
            "Problem Decomposition",
            "Root Cause Analysis",
            "Research Skills",
            "Outcome Reflection",
        ],
        has_follow_up=True,
    ),

    # =========================================================================
    # PROJECT  (5 questions)
    # =========================================================================

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.PROJECT,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "Tell me about a backend project you have built. "
            "What problem did it solve and what technologies did you use?"
        ),
        skills=["Backend Development", "Project Design"],
        technologies=["Python", "FastAPI", "PostgreSQL"],
        expected_concepts=[
            "Problem Statement",
            "Technology Choice Rationale",
            "Architecture Overview",
            "Outcome",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.PROJECT,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "How did you handle user authentication in your project? "
            "Walk me through the implementation from registration to protected endpoint access."
        ),
        skills=["Security", "API Development", "Backend Development"],
        technologies=["FastAPI", "JWT", "bcrypt", "python-jose"],
        expected_concepts=[
            "Password Hashing",
            "JWT Issuance",
            "Token Verification",
            "Protected Routes",
            "Dependency Injection",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.PROJECT,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "If you could rebuild your backend project from scratch, "
            "what architectural or technical decisions would you change and why?"
        ),
        skills=["Software Architecture", "Critical Thinking", "Backend Development"],
        technologies=["Python"],
        expected_concepts=[
            "Architectural Trade-offs",
            "Lessons Learned",
            "Scalability Thinking",
            "Code Quality Reflection",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.PROJECT,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "How did you design and version your database schema in your project? "
            "How did you handle schema changes over time?"
        ),
        skills=["Database Design", "Backend Development"],
        technologies=["PostgreSQL", "SQLAlchemy", "Alembic"],
        expected_concepts=[
            "Schema Design",
            "Database Migrations",
            "Version Control for Schema",
            "Backward Compatibility",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.PROJECT,
        difficulty=DifficultyLevel.HARD,
        question_text=(
            "Describe a situation in your project where a feature worked locally "
            "but broke in a different environment. "
            "How did you diagnose and fix it?"
        ),
        skills=["Debugging", "DevOps", "Backend Development"],
        technologies=["Docker", "Python", "Git"],
        expected_concepts=[
            "Environment Parity",
            "Configuration Management",
            "Debugging Strategy",
            "Containerisation",
            "Environment Variables",
        ],
        has_follow_up=True,
    ),

    # =========================================================================
    # TECHNICAL  (13 questions)
    # =========================================================================

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is the difference between GET, POST, PUT, PATCH, and DELETE "
            "HTTP methods? When would you use each?"
        ),
        skills=["API Development", "HTTP"],
        technologies=["HTTP", "REST"],
        expected_concepts=[
            "Idempotency",
            "Safe Methods",
            "Resource Creation vs Update",
            "Partial vs Full Update",
            "HTTP Semantics",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What are HTTP status codes and why do they matter in API design? "
            "Give examples of when you would return 200, 201, 400, 401, 403, 404, and 500."
        ),
        skills=["API Design", "HTTP"],
        technologies=["HTTP", "REST", "FastAPI"],
        expected_concepts=[
            "2xx Success",
            "4xx Client Errors",
            "5xx Server Errors",
            "Semantic Correctness",
            "Client Guidance",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "Explain how a JWT token works. "
            "What are its three parts and what information does each contain?"
        ),
        skills=["Security", "Authentication"],
        technologies=["JWT", "python-jose"],
        expected_concepts=[
            "Header",
            "Payload",
            "Signature",
            "Base64 Encoding",
            "HMAC Signing",
            "Statelessness",
            "Expiry",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is the difference between a database index and a full table scan? "
            "When would you add an index and what are the trade-offs?"
        ),
        skills=["Database Optimisation", "SQL"],
        technologies=["PostgreSQL", "SQLAlchemy"],
        expected_concepts=[
            "B-Tree Index",
            "Query Performance",
            "Write Overhead",
            "Cardinality",
            "Index on Foreign Keys",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "What is SQLAlchemy's ORM session and how does it manage the "
            "database transaction lifecycle? "
            "Explain the difference between flush and commit."
        ),
        skills=["Database", "Python", "ORM"],
        technologies=["SQLAlchemy", "PostgreSQL"],
        expected_concepts=[
            "Unit of Work Pattern",
            "Identity Map",
            "flush() vs commit()",
            "rollback()",
            "Session Scope",
            "Transaction Isolation",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain FastAPI's dependency injection system. "
            "How would you use it to provide a database session to every endpoint "
            "and ensure the session is always closed after the request?"
        ),
        skills=["FastAPI", "API Development", "Python"],
        technologies=["FastAPI", "SQLAlchemy"],
        expected_concepts=[
            "Depends()",
            "Generator Dependencies",
            "Session Lifecycle",
            "yield in Dependencies",
            "Teardown on Error",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "What is the N+1 query problem in ORM-based applications? "
            "How would you detect it and what strategies would you use to fix it in SQLAlchemy?"
        ),
        skills=["Database Optimisation", "ORM", "Performance"],
        technologies=["SQLAlchemy", "PostgreSQL"],
        expected_concepts=[
            "Lazy Loading",
            "Eager Loading",
            "joinedload",
            "selectinload",
            "SQL Logging",
            "Query Count",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "What is Python's asyncio and how does async/await work? "
            "When would you use async endpoints in FastAPI versus synchronous ones?"
        ),
        skills=["Async Programming", "Python", "FastAPI"],
        technologies=["Python", "asyncio", "FastAPI"],
        expected_concepts=[
            "Event Loop",
            "Coroutines",
            "Non-blocking I/O",
            "CPU-bound vs IO-bound",
            "Threadpool Fallback",
            "await Keyword",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "What is database normalisation? "
            "Explain 1NF, 2NF, and 3NF with a practical example. "
            "When might you intentionally denormalise?"
        ),
        skills=["Database Design", "SQL"],
        technologies=["PostgreSQL"],
        expected_concepts=[
            "First Normal Form",
            "Second Normal Form",
            "Third Normal Form",
            "Functional Dependency",
            "Denormalisation Trade-offs",
            "Read Performance vs Write Integrity",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain how Git branching strategies work in a team setting. "
            "How would you handle a hotfix on production while a feature branch is in progress?"
        ),
        skills=["Git", "Version Control", "Team Collaboration"],
        technologies=["Git", "GitHub"],
        expected_concepts=[
            "Feature Branch",
            "Main/Master Branch",
            "Hotfix Branch",
            "Merge vs Rebase",
            "Pull Requests",
            "Conflict Resolution",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.HARD,
        question_text=(
            "A FastAPI endpoint that queries the database is responding slowly under load. "
            "Walk me through your diagnostic process and the optimisations you would apply."
        ),
        skills=["Performance", "Database Optimisation", "Backend Development"],
        technologies=["FastAPI", "PostgreSQL", "SQLAlchemy"],
        expected_concepts=[
            "Query Profiling",
            "EXPLAIN ANALYZE",
            "Index Strategy",
            "Connection Pooling",
            "Caching Layer",
            "Async Queries",
            "Pagination",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.HARD,
        question_text=(
            "Explain what a database transaction is and what ACID properties mean. "
            "Write a SQLAlchemy example that creates a user and their profile atomically, "
            "rolling back both if either fails."
        ),
        skills=["Database", "Python", "Backend Development"],
        technologies=["SQLAlchemy", "PostgreSQL"],
        expected_concepts=[
            "Atomicity",
            "Consistency",
            "Isolation",
            "Durability",
            "try/except/rollback",
            "db.flush()",
            "Atomic Multi-table Write",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.HARD,
        question_text=(
            "What is caching and how would you implement a simple cache for an expensive "
            "database query in a FastAPI application? "
            "What are the cache invalidation challenges you would need to handle?"
        ),
        skills=["Caching", "Performance", "Backend Development"],
        technologies=["Redis", "FastAPI", "Python"],
        expected_concepts=[
            "Cache Hit vs Miss",
            "TTL",
            "Cache Invalidation",
            "Stale Data",
            "In-memory vs Distributed Cache",
            "Cache Stampede",
        ],
        has_follow_up=True,
    ),

    # =========================================================================
    # ROLE_SPECIFIC  (5 questions)
    # =========================================================================

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is Docker and why is it useful for backend development? "
            "Explain the difference between a Docker image and a Docker container."
        ),
        skills=["DevOps", "Containerisation", "Backend Development"],
        technologies=["Docker", "Docker Compose"],
        expected_concepts=[
            "Image as Blueprint",
            "Container as Running Instance",
            "Environment Isolation",
            "Portability",
            "docker-compose for Local Dev",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Design a RESTful API for a blog platform with posts, comments, and authors. "
            "Define the resource URLs, HTTP methods, and status codes for the core operations."
        ),
        skills=["API Design", "REST", "Backend Development"],
        technologies=["FastAPI", "HTTP", "REST"],
        expected_concepts=[
            "Resource Naming",
            "Nested Resources",
            "CRUD Mapping to HTTP Methods",
            "Status Codes",
            "Pagination",
            "Filtering",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "How would you write a unit test for a FastAPI endpoint that creates a user? "
            "What would you mock and why?"
        ),
        skills=["Testing", "Python", "FastAPI"],
        technologies=["pytest", "FastAPI", "httpx"],
        expected_concepts=[
            "TestClient",
            "Dependency Override",
            "Mock Database Session",
            "Arrange-Act-Assert",
            "Test Isolation",
            "Status Code Assertion",
            "Response Body Assertion",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.HARD,
        question_text=(
            "How would you design a rate limiting system for a public REST API "
            "to protect it from abuse? Describe the algorithm, storage layer, "
            "and how you would return meaningful errors to the client."
        ),
        skills=["API Design", "Security", "Backend Development"],
        technologies=["Redis", "FastAPI", "Python"],
        expected_concepts=[
            "Token Bucket Algorithm",
            "Fixed Window vs Sliding Window",
            "Redis for Counter Storage",
            "HTTP 429 Too Many Requests",
            "Retry-After Header",
            "Per-User vs Per-IP Limits",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.HARD,
        question_text=(
            "A user reports that their data appeared in another user's API response. "
            "Describe how this kind of data leakage can happen in a backend system "
            "and how you would prevent and detect it."
        ),
        skills=["Security", "API Development", "Backend Development"],
        technologies=["FastAPI", "SQLAlchemy", "PostgreSQL"],
        expected_concepts=[
            "Broken Object Level Authorisation",
            "OWASP API Security",
            "Ownership Checks",
            "Row-Level Security",
            "Audit Logging",
            "Automated Security Testing",
        ],
        has_follow_up=True,
    ),

    # =========================================================================
    # BEHAVIORAL  (3 questions)
    # =========================================================================

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.BEHAVIORAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "Describe a time you were stuck on a technical problem for a long time. "
            "How did you eventually resolve it and what did you learn?"
        ),
        skills=["Problem Solving", "Persistence", "Learning Mindset"],
        technologies=[],
        expected_concepts=[
            "Systematic Debugging",
            "Seeking Help",
            "Documentation Reading",
            "Root Cause Identification",
            "Lesson Extraction",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.BEHAVIORAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Tell me about a time you received critical feedback on code you wrote. "
            "How did you respond to it and what did you change?"
        ),
        skills=["Feedback Reception", "Growth Mindset", "Team Collaboration"],
        technologies=[],
        expected_concepts=[
            "Openness to Feedback",
            "Code Review Culture",
            "Implementing Suggestions",
            "Professional Maturity",
            "Continuous Improvement",
        ],
        has_follow_up=True,
    ),

    create_question(
        role=_ROLE,
        experience_level=_LEVEL,
        category=QuestionCategory.BEHAVIORAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "How do you approach learning a new framework or technology that you "
            "need to use in a project but have never worked with before?"
        ),
        skills=["Learning Strategy", "Self-directed Learning", "Adaptability"],
        technologies=[],
        expected_concepts=[
            "Official Documentation",
            "Minimal Working Example",
            "Incremental Adoption",
            "Community Resources",
            "Time Management",
        ],
        has_follow_up=False,
    ),
]
