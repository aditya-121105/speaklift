# SpeakLift: Error Recovery

In a cloud-dependent AI application, network requests will occasionally fail. The frontend must be designed to fail gracefully, ensuring the user never loses their progress.

## 1. Resume Parsing Failure
- **Scenario**: User uploads a highly customized PDF that the backend PDF miner fails to read.
- **Recovery**: Do not block onboarding. 
- **UI**: "We had trouble reading this specific PDF format. Don't worry, you can manually enter your top 3 skills below to get started."

## 2. Interview Interruption (Network Drop)
- **Scenario**: User submits an answer, but their Wi-Fi drops before the AI responds.
- **Recovery**:
  - The API client detects a network timeout (or offline event).
  - The active answer is cached immediately in `localStorage` or IndexedDB.
  - The UI transitions the "Submit" button to a "Network Offline - Retrying..." state.
  - When connection is restored, the `useMutation` hook automatically retries the submission.
  - If the user refreshes the page, the active session is rehydrated from the backend (since sessions are created in the DB prior to question 1).

## 3. Streaming Interruption
- **Scenario**: An AI report is streaming into the UI, but the connection drops halfway through.
- **Recovery**:
  - The UI detects the stream closure without an EOF token.
  - It displays an inline, non-intrusive warning: "Connection lost. Reconnecting to finish your report..."
  - A background fetch triggers to retrieve the completed report from the database (assuming the backend finished generating it).

## 4. Authentication Expiration
- **Scenario**: The user is halfway through typing an answer, and their JWT expires.
- **Recovery**:
  - The frontend MUST NOT redirect them to `/login` immediately, as this would destroy their un-submitted text.
  - The Axios interceptor catches the 401.
  - It pauses the API call.
  - It pops up a modal over the active screen: "Your session expired. Please enter your password to continue."
  - Upon successful re-auth, the modal closes, and the original API call is retried transparently.

## 5. Global Fallback (Error Boundary)
- **Scenario**: An unhandled frontend React exception occurs (e.g., a chart fails to render due to malformed data).
- **Recovery**:
  - The React `<ErrorBoundary>` catches the crash at the Feature Module level, NOT the root level.
  - The rest of the dashboard remains perfectly functional.
  - The broken widget displays a clean fallback UI: "We couldn't load this chart." with a "Retry" button.
