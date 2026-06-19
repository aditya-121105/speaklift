# app/shared/enums.py

from enum import Enum


class InterviewStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class ExperienceLevel(str, Enum):
    STUDENT = "STUDENT"
    FRESHER = "FRESHER"
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"

class QuestionType(str, Enum):
    PRIMARY = "PRIMARY"
    FOLLOW_UP = "FOLLOW_UP"


class QuestionCategory(str, Enum):
    INTRODUCTION = "INTRODUCTION"
    PROJECT = "PROJECT"
    TECHNICAL = "TECHNICAL"
    ROLE_SPECIFIC = "ROLE_SPECIFIC"
    BEHAVIORAL = "BEHAVIORAL"

class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class QuestionSource(str, Enum):
    AI = "AI"
    MANUAL = "MANUAL"
class AnswerSource(str, Enum):
    TEXT = "TEXT"
    VOICE = "VOICE"