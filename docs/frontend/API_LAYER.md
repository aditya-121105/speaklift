# SpeakLift: API Layer Architecture

All network communication between the frontend and backend must go through a centralized, deeply configurable API client. Raw `fetch()` or `axios.get()` calls within UI components are strictly forbidden.

## 1. Centralized Axios Client (`src/lib/api-client.ts`)
We use Axios due to its robust interceptor support, automatic JSON transformation, and cancellation token capabilities.

- **Base URL**: Managed via environment variables (`NEXT_PUBLIC_API_URL`).
- **Timeouts**: Enforce a strict `10000ms` default timeout for standard requests. Long-running requests (e.g., waiting for AI generation) must explicitly override this timeout via their specific Service method.

## 2. Interceptors

### Request Interceptor
- **Authentication**: Automatically attaches the JWT `Authorization: Bearer <token>` to every outbound request (if the token exists).
- **Correlation**: Attaches an `X-Client-Trace-Id` to trace frontend events to backend logs.

### Response Interceptor
- **Error Normalization**: Transforms non-200 responses into a standardized frontend `ApiError` class. This ensures TanStack Query always receives a predictable error object containing the `error_code`, `message`, and `status`.
- **401 Unauthorized Handling**: Detects expired tokens. Triggers a global logout action and redirects to `/login` seamlessly.

## 3. Retry Strategy
- Handled primarily by TanStack Query, configured globally in `app/layout.tsx`.
- **Idempotent Requests (GET)**: Automatically retried up to 3 times with exponential backoff on network failure or 503 Service Unavailable errors.
- **Mutations (POST/PUT/DELETE)**: Never retried automatically to prevent duplicate transactions.

## 4. Cancellation Strategy
- If a user navigates away from a page while a slow request is pending, the request should be aborted to free up browser connections.
- Achieved by passing TanStack Query's `signal` to the Axios request configuration.

## 5. Streaming Compatibility
- While Axios handles JSON APIs perfectly, it is not ideal for Server-Sent Events (SSE) or Web Streams.
- For streaming endpoints (e.g., real-time AI transcription or generation), a dedicated Service method will utilize the native `fetch` API and Web Streams API (`ReadableStream`), bypassing Axios entirely for that specific capability.

## 6. API Services
Domain services wrap the Axios client.

```typescript
// Example: src/features/interviews/api/interview-service.ts
export const InterviewService = {
  getReport: async (id: string): Promise<InterviewReport> => {
    const response = await apiClient.get(`/v1/interviews/${id}/report`);
    return response.data;
  },
  submitAnswer: async (id: string, payload: SubmitAnswerDto) => {
    // Overrides timeout for heavy AI evaluation
    const response = await apiClient.post(`/v1/interviews/${id}/answers`, payload, { timeout: 30000 });
    return response.data;
  }
};
```
