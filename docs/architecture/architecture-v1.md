# Architecture v1

## Overview

AI Interview & Viva Simulator is a production-style AI platform that enables users to practice interviews and viva examinations through AI-driven conversations.

The system is designed using a Modular Monolith architecture with clear module boundaries and future microservice extraction in mind.

Primary goals:

- Interview simulation
- Viva simulation
- Communication analysis
- Answer evaluation
- Progress tracking
- AI-powered feedback

## Architecture Style

Architecture Pattern:
Modular Monolith

Reasoning:

- Faster development
- Easier debugging
- Lower operational complexity
- Easier deployment
- Supports future migration to microservices

## High-Level Components

Frontend
- React
- TypeScript
- TailwindCSS

Backend
- FastAPI
- SQLAlchemy
- Alembic

Database
- PostgreSQL

AI Layer
- Whisper
- Sentence Transformers
- LLM Provider Layer

Cloud
- AWS
## Backend Modules

### Auth Module

Responsibilities:
- Registration
- Login
- JWT Authentication

---

### Interview Module

Responsibilities:
- Interview creation
- Interview management
- Question flow

---

### Viva Module

Responsibilities:
- Viva generation
- Topic handling
- Academic evaluation

---

### Speech Module

Responsibilities:
- Audio upload
- Transcription
- Transcript storage

---

### Evaluation Module

Responsibilities:
- Answer evaluation
- Communication scoring
- Semantic analysis

---

### Analytics Module

Responsibilities:
- Progress tracking
- Dashboard generation
- Historical analysis

---

### Vision Module

Responsibilities:
- Eye contact analysis
- Head pose analysis
- Engagement scoring

---

### Avatar Module

Responsibilities:
- Interviewer avatar integration

## AI Layer

The AI layer is separated from application business logic.

Components:

### Speech Processing

Model:
Whisper

Purpose:
Audio → Text

---

### Embedding Layer

Model:
all-MiniLM-L6-v2

Purpose:
Semantic similarity
Answer relevance scoring

---

### LLM Layer

Provider Abstraction

Supported Providers:

- Ollama
- OpenAI
- Gemini
- Claude

Purpose:
Question generation
Follow-up generation
Feedback generation


## Request Flow

User

↓

React Frontend

↓

FastAPI API

↓

Service Layer

↓

Repository Layer

↓

PostgreSQL

OR

↓

AI Layer

↓

Response


## Scalability Strategy

Current:
Modular Monolith

Future:

Possible extraction:

- Speech Service
- Vision Service
- Evaluation Service

No architecture changes should be required when extracting these modules.


## Deployment Architecture

Development

Docker Compose

Containers:

- backend
- postgres

Production

AWS

Services:

- EC2
- RDS PostgreSQL
- S3
- CloudWatch
- IAM

## Design Principles

- Separation of Concerns
- Single Responsibility Principle
- Dependency Injection
- Provider Abstraction
- API Versioning
- Configuration Driven Design
- Cloud Readiness