# SpeakLift Backend: Production Engineering

## Operational Philosophy

SpeakLift is designed to run in highly concurrent, containerized cloud environments. 

- **Stateless Application Nodes**: The backend instances hold no sticky state. Inter-request orchestration relies purely on PostgreSQL and the client-supplied JWT.
- **Fail Fast**: Misconfigurations during startup crash the process instantly, preventing "zombie" nodes from accepting traffic they cannot route.
- **Observability First**: We rely on extensive structured logging and Correlation IDs for distributed tracing rather than heavy APM sidecars when possible.

## Production Engineering Roadmap

### Sprint PE1 (Observability & Runtime Foundation) - **Completed**
- Implementation of Structured JSON Logging.
- Implementation of `CorrelationIdMiddleware` for `X-Request-ID` and latency tracking.
- Health Probes (`/api/v1/health/live`, `/api/v1/health/ready`).
- Application lifespan controls (startup config validation, graceful db shutdown).

### Sprint PE2 (Security & Reliability) - **Completed**
- Global Exception Handler generating consistent JSON schemas.
- CORS Configuration and `TrustedHostMiddleware`.
- `SecurityHeadersMiddleware` (CSP, X-Frame-Options, HSTS).
- `RequestSizeLimitMiddleware` (max 15MB).
- `RateLimitMiddleware` (fixed window IP-based rate limiting).

### Sprint PE3 (Caching & Performance) - **Planned**
- Implementation of `Redis` for caching transient states (e.g., Job Descriptions, prompt caching).
- Pre-computation warming hooks for SpaCy / BGE models.

### Sprint PE4 (Deployment Automation) - **Planned**
- CI/CD Pipelines (GitHub Actions / GitLab CI).
- Dockerfile optimizations.
- Kubernetes Manifests (Deployments, HPA, Services).

---

## Observability

### Logging
- **Format**: NDJSON (Newline Delimited JSON).
- **Tooling**: Emitted via `app/core/logging.py` overriding standard `uvicorn` loggers.
- **Context**: Every log is automatically bound with `request_id` via Python `ContextVars`.

### Tracing
- The API responds with `X-Request-ID` headers to correlate client activity with backend logs.
- The `X-Process-Time` header reports absolute latency bounds across the ASGI gateway.

## Health Checks
Orchestration systems (Kubernetes) should use the following:
- **Liveness**: `GET /api/v1/health/live` ensures the event loop is not deadlocked.
- **Readiness**: `GET /api/v1/health/ready` ensures DB is connected and capable of answering requests.

## Security
- Secrets (`GEMINI_API_KEY`, `JWT_SECRET_KEY`) must be securely injected via environment variables (`.env` in dev, Vault/K8s Secrets in production).
- Configuration parameters are mapped cleanly via `pydantic-settings`.

## Runtime
- The application executes using `uvicorn` natively or combined with `gunicorn` workers for process management depending on the deployment density.
