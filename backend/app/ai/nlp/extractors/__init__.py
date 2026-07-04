# backend/app/ai/nlp/extractors/__init__.py
"""
NLP Extractors
==============

Domain-specific entity extractors for resume and job description parsing.

Each extractor receives processed NLP output and returns a typed,
structured result for a specific information category.

Planned extractors
------------------
SkillExtractor        (Sprint C.3) — programming languages, frameworks, tools
TechnologyExtractor   (Sprint C.3) — cloud platforms, databases, DevOps tools
EducationExtractor    (Sprint C.3) — degrees, institutions, graduation years
ExperienceExtractor   (Sprint C.3) — job titles, companies, date ranges
ProjectExtractor      (Sprint C.3) — projects, descriptions, tech stacks
ContactExtractor      (Sprint C.4) — name, email, phone, LinkedIn URL

Architecture rules
------------------
- Each extractor is INDEPENDENT — it knows nothing about the others.
- Extractors produce ONLY structured data. No scoring, ranking, or decisions.
- All extractors implement a common abstract interface (to be defined in C.3).
- Extractors are composed by the NLP pipeline service, not called directly
  from business services.

Sprint C.2 — package skeleton only.
"""
