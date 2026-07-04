# backend/app/ai/llm/prompts/__init__.py
"""
LLM Prompt Templates
=====================

Typed, versioned prompt builders for every LLM use case in SpeakLift.

Design rules
------------
1. ALL prompt strings are built here. No inline f-strings for prompts
   anywhere in services/, endpoints/, or providers/.
2. Every prompt template is VERSIONED. When a prompt changes, the old
   version is kept (with a deprecation note) until confirmed safe to remove.
3. Templates are PURE FUNCTIONS or PURE CLASSES — they produce strings
   given inputs. No I/O, no database access, no AI calls.
4. Templates document their expected variables, output format, and the
   model family they are tuned for.

Planned templates
-----------------
QuestionGenerationPrompt    (Sprint C.5)
    Use case : Generate interview questions from a candidate profile
               and job description.
    Variables: role, skills, difficulty, question_count, context
    Output   : Structured JSON list of question objects

FeedbackGenerationPrompt    (Sprint C.5)
    Use case : Generate qualitative feedback on a candidate's answer.
    Variables: question, answer, rubric, tone
    Output   : Free-text feedback with improvement suggestions

ResumeInsightPrompt         (Sprint C.5)
    Use case : Extract narrative insights from parsed resume text.
    Variables: resume_text, target_role
    Output   : Structured JSON profile enrichment

InterviewSummaryPrompt      (Sprint C.6)
    Use case : Summarise a completed interview session.
    Variables: session_id, questions_and_answers, evaluation_scores
    Output   : Human-readable session summary

Sprint C.2 — skeleton only. No templates implemented.
"""
