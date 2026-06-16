# Database Design v1

## Overview

SpeakLift uses PostgreSQL as its primary relational database.

The database is designed to support:

* User management
* Interview sessions
* Viva sessions
* Question management
* Response storage
* Speech transcription
* AI-powered evaluation
* Progress tracking
* Personalized recommendations
* Future speech and vision analytics

The schema follows normalization principles while remaining practical for analytics, reporting, and future scalability.

---

# Database Technology

Database: PostgreSQL

ORM: SQLAlchemy 2.x

Migration Tool: Alembic

Primary Key Strategy: UUID

---

# Design Principles

* Use UUID primary keys
* Use foreign key constraints
* Support auditability
* Support analytics and reporting
* Support future AI modules
* Minimize schema redesign in future versions
* Store historical data whenever possible
* Prioritize long-term progress tracking
* Design for realistic interview simulation

---

# Core Entities

users

profiles

interview_sessions

viva_sessions

question_bank

questions

responses

transcripts

evaluations

session_analytics

recommendations

user_progress

---

# Entity Relationships

User
│
├── Profile
│
├── Interview Sessions
│   ├── Questions
│   ├── Responses
│   ├── Evaluations
│   └── Session Analytics
│
├── Viva Sessions
│   ├── Questions
│   ├── Responses
│   ├── Evaluations
│   └── Session Analytics
│
├── Recommendations
│
└── User Progress

Question Bank
│
└── Questions

Question
│
└── Response

Response
│
├── Transcript
│
└── Evaluation

---

# users

Purpose:

Stores authentication and account information.

Columns:

id UUID PRIMARY KEY

email VARCHAR(255) UNIQUE NOT NULL

password_hash TEXT NOT NULL

is_active BOOLEAN DEFAULT TRUE

created_at TIMESTAMP

updated_at TIMESTAMP

Indexes:

UNIQUE(email)

Notes:

Email must be unique across the platform.

---

# profiles

Purpose:

Stores user profile information.

Columns:

id UUID PRIMARY KEY

user_id UUID UNIQUE REFERENCES users(id)

full_name VARCHAR(255)

education VARCHAR(255)

target_role VARCHAR(255)

experience_level VARCHAR(50)

created_at TIMESTAMP

updated_at TIMESTAMP

Relationship:

One Profile belongs to one User.

---

# interview_sessions

Purpose:

Stores interview practice sessions.

Columns:

id UUID PRIMARY KEY

user_id UUID REFERENCES users(id)

target_role VARCHAR(255)

experience_level VARCHAR(50)

difficulty VARCHAR(50)

status VARCHAR(50)

started_at TIMESTAMP

ended_at TIMESTAMP NULL

created_at TIMESTAMP

updated_at TIMESTAMP

---

# viva_sessions

Purpose:

Stores viva practice sessions.

Columns:

id UUID PRIMARY KEY

user_id UUID REFERENCES users(id)

subject VARCHAR(255)

topic VARCHAR(255)

difficulty VARCHAR(50)

status VARCHAR(50)

started_at TIMESTAMP

ended_at TIMESTAMP NULL

created_at TIMESTAMP

updated_at TIMESTAMP

---

# question_bank

Purpose:

Stores reusable interview and viva questions.

Columns:

id UUID PRIMARY KEY

question_text TEXT NOT NULL

question_type VARCHAR(50)

category VARCHAR(100)

topic VARCHAR(100)

difficulty VARCHAR(50)

target_roles JSONB NULL

subject VARCHAR(100) NULL

is_active BOOLEAN DEFAULT TRUE

times_used INTEGER DEFAULT 0

created_at TIMESTAMP

updated_at TIMESTAMP

Examples:

question_type:

* INTERVIEW
* VIVA
* FOLLOW_UP

target_roles:

[
"AI/ML Engineer",
"Data Scientist"
]

---

# questions

Purpose:

Stores questions asked during a specific session.

Columns:

id UUID PRIMARY KEY

question_bank_id UUID NULL REFERENCES question_bank(id)

interview_session_id UUID NULL REFERENCES interview_sessions(id)

viva_session_id UUID NULL REFERENCES viva_sessions(id)

question_text TEXT

generated_by_ai BOOLEAN DEFAULT FALSE

sequence_no INTEGER

asked_at TIMESTAMP

Notes:

A question belongs to either an Interview Session or a Viva Session.

Question history is preserved and never deleted.

---

# responses

Purpose:

Stores user answers to interview and viva questions.

Columns:

id UUID PRIMARY KEY

question_id UUID REFERENCES questions(id)

response_type VARCHAR(20)

response_text TEXT

audio_url TEXT NULL

response_duration_seconds INTEGER NULL

created_at TIMESTAMP

updated_at TIMESTAMP

Examples:

response_type:

* TEXT
* AUDIO
* VIDEO

---

# transcripts

Purpose:

Stores speech-to-text results.

Columns:

id UUID PRIMARY KEY

response_id UUID REFERENCES responses(id)

transcript_text TEXT

language VARCHAR(20)

confidence_score FLOAT

created_at TIMESTAMP

Notes:

Transcripts are stored separately from responses to allow future reprocessing with improved speech models.

---

# evaluations

Purpose:

Stores AI-generated evaluation results.

Columns:

id UUID PRIMARY KEY

response_id UUID REFERENCES responses(id)

grammar_score FLOAT

vocabulary_score FLOAT

fluency_score FLOAT

confidence_score FLOAT

relevance_score FLOAT

professionalism_score FLOAT

overall_score FLOAT

strengths JSONB

improvements JSONB

feedback TEXT

model_version VARCHAR(50)

raw_evaluation JSONB

created_at TIMESTAMP

Notes:

Stores both processed scores and raw AI outputs for future debugging, auditing, and model improvements.

---

# session_analytics

Purpose:

Stores aggregated performance metrics for a complete interview or viva session.

Columns:

id UUID PRIMARY KEY

interview_session_id UUID NULL

viva_session_id UUID NULL

overall_score FLOAT

communication_score FLOAT

confidence_score FLOAT

technical_score FLOAT

total_questions INTEGER

answered_questions INTEGER

created_at TIMESTAMP

Notes:

Represents session-level performance rather than individual response evaluation.

---

# recommendations

Purpose:

Stores personalized improvement recommendations.

Columns:

id UUID PRIMARY KEY

user_id UUID REFERENCES users(id)

session_analytics_id UUID REFERENCES session_analytics(id)

recommendation_type VARCHAR(50)

priority VARCHAR(20)

recommendation_text TEXT

metadata JSONB

created_at TIMESTAMP

Examples:

recommendation_type:

* CONFIDENCE
* COMMUNICATION
* TECHNICAL
* PROJECT_EXPLANATION

priority:

* LOW
* MEDIUM
* HIGH

---

# user_progress

Purpose:

Stores long-term user performance metrics.

Columns:

id UUID PRIMARY KEY

user_id UUID REFERENCES users(id)

communication_score FLOAT

confidence_score FLOAT

professionalism_score FLOAT

overall_score FLOAT

total_sessions INTEGER

last_session_at TIMESTAMP

updated_at TIMESTAMP

Notes:

Used for dashboard statistics, historical tracking, and progress visualization.

---

# Future Expansion

Possible future tables:

resumes

resume_projects

vision_analytics

avatar_sessions

career_plans

resource_recommendations

---

# Future Vision

Future versions of SpeakLift will support:

* Resume-based interview personalization
* Eye-contact analysis
* Head-pose analysis
* Facial-expression analysis
* AI interviewer avatars
* Real-time voice interactions
* Advanced coaching recommendations

The current schema is designed to support these features without requiring major database redesign.
