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


class StorageProvider(str, Enum):
    LOCAL = "LOCAL"
    S3 = "S3"
    AZURE = "AZURE"
    GCS = "GCS"


class UploadStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ParsingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
class AnswerSource(str, Enum):
    TEXT = "TEXT"
    VOICE = "VOICE"
class EvaluationSource(
    str,
    Enum,
):
    RULE_BASED = "RULE_BASED"

    GEMINI = "GEMINI"

    ML = "ML"

    HYBRID = "HYBRID"