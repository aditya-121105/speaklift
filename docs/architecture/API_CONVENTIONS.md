# SpeakLift Backend: API Conventions

## 1. REST Conventions
- **Nouns over Verbs**: Use nouns representing resources (`/interviews`, `/resumes`).
- **Nesting**: Use hierarchical relations correctly (`/interviews/{id}/report`, `/interviews/{id}/questions`).
- **Pluralization**: Resource collections should be pluralized (`/api/v1/interviews`).

## 2. Status Codes
- `200 OK`: Successful synchronous operations (GET, PUT, DELETE).
- `201 Created`: Successful POST operations resulting in resource generation.
- `400 Bad Request`: Validation failure on business logic constraints.
- `401 Unauthorized`: Missing or invalid JWT.
- `403 Forbidden`: User attempts to access a resource they do not own.
- `404 Not Found`: Resource ID does not exist.
- `422 Unprocessable Entity`: Request body violates schema types (handled automatically by FastAPI).
- `503 Service Unavailable`: Dependent upstream services (e.g., database, Gemini API) are offline.

## 3. Error Model
Errors returned to the client must follow a standard JSON envelope (provided via `exception_handlers.py`):
```json
{
  "error": {
    "code": "INTERVIEW_NOT_FOUND",
    "message": "The specified interview session does not exist."
  }
}
```
Stack traces are exclusively printed to backend logs and must never leak via the API.

## 4. Validation
- **Input Validation**: Dictated entirely by Pydantic models inside `app.schemas`.
- **Security Validation**: Fast API dependency injection `Depends(get_current_user)` inherently enforces authorization. Ownership (e.g., checking if user A owns Session B) is enforced synchronously at the top of the endpoint prior to invoking any Business Service logic.

## 5. Response Format
- Wrap object outputs if needed, but commonly Pydantic objects are returned directly by FastAPI in standard JSON serialization.
- For collections, return arrays.

## 6. Versioning
- All endpoints are prefixed with `/api/v1/`.
- Breaking changes require deploying a parallel `/api/v2/` namespace to guarantee backwards compatibility.

## 7. Pagination
- Endpoints fetching collections (e.g., historical interviews) must eventually utilize `limit` and `skip` query parameters.

## 8. Future Compatibility
- To avoid breaking changes, use optional fields when extending request schemas. 
- Avoid changing field types on existing endpoints. 
