# backend/app/ai/recommendations/__init__.py
"""
AI Recommendations
==================

Responsible for generating personalised learning recommendations
based on candidate performance data.

Architecture position
---------------------
Interview Evaluation Results
    │
    ├──▶ Pattern Analysis (rule-based, Sprint C.6)
    │        — identify consistent weaknesses across sessions
    │
    ├──▶ ML Ranking (Sprint C.6)
    │        — prioritise recommendations by expected improvement impact
    │
    └──▶ LLM Generation (optional, Sprint C.7)
             — generate human-readable improvement suggestions

Planned components
------------------
RecommendationEngine   (Sprint C.6)
    — Combines pattern analysis and ML ranking to produce a ranked list
    — of improvement recommendations for a candidate.

SkillGapAnalyser       (Sprint C.6)
    — Compares candidate skill profile against target role requirements
    — and identifies the highest-priority gaps.

LearningPathBuilder    (Sprint C.7)
    — Uses LLMService to generate a structured learning path from gaps.

Engineering note
----------------
Follow the Complexity Gradient: use rule-based gap detection first.
Add ML ranking only if rule-based prioritisation is demonstrably insufficient.
Reserve LLM for narrative generation only.

Sprint C.2 — skeleton only.
Sprint C.6 — implement RecommendationEngine and SkillGapAnalyser.
"""
