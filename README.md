# SpeakLift

Speak with Confidence. Lift Your Career.

AI-Powered Interview & Viva Confidence Platform

AI-powered communication improvement platform focused on interview preparation, speaking confidence, professional communication, and personalized coaching.

## Vision

Help users transform English knowledge into communication confidence.

## Planned Features

- Speaking practice
- Interview simulation
- Viva preparation
- Communication analysis
- Confidence evaluation
- Vocabulary enhancement
- Personalized improvement roadmap
- Analytics dashboard

## Project Status

Planning & Architecture Phase

## Repository Structure

```text
frontend/         Frontend application
backend/          Backend APIs
infrastructure/   Cloud and deployment resources
docs/             Architecture and documentation
tests/            Test suites
scripts/          Utility scripts
```

## AI Architecture

SpeakLift implements a provider-agnostic AI layer supporting both cloud and local inference:
- **Provider-agnostic AI layer**: The business layer communicates via a unified `LLMService`.
- **Gemini**: Supported cloud provider for robust inference.
- **Ollama**: Supported local provider for cost-free, private development.
- **Router**: Automatic configuration-driven failover between cloud and local models.
- **Local-first development**: We encourage local development using Ollama (Qwen 3).
- **Cloud fallback**: Automatic fallback to Gemini based on routing strategy.

## Goals

- Learn practical AI/ML
- Learn cloud deployment
- Build industry-style software
- Prepare for placements and interviews