# SpeakLift: Decision Trees

This document maps the logical branches the frontend must evaluate during critical user flows.

## 1. Resume Upload Decision Tree
**Trigger**: User clicks "Upload Resume" in onboarding or profile.
1. **File Selected**
   - *Is size > 10MB?*
     - Yes -> Show Error Toast ("File too large"). Halt.
     - No -> Proceed.
   - *Is type PDF or DOCX?*
     - No -> Show Error Toast ("Unsupported format"). Halt.
     - Yes -> Proceed.
2. **Upload & Parse**
   - Show loading skeleton for "Extracting Skills".
   - *Did API return 200 OK?*
     - Yes -> Show success animation. Update `useAuth` context with new resume metadata.
     - No -> Show fallback UI ("We couldn't parse this automatically. Please enter skills manually.")

## 2. Interview Creation Logic
**Trigger**: User clicks "Start New Interview".
1. **JD Input Method**
   - *Did user paste text or skip?*
     - If Skip -> Fallback to "General Software Engineering" default profile.
     - If Text -> Send to `/v1/job-descriptions/parse`.
2. **Interview Generation**
   - Send JD ID and Resume ID (if available) to `/v1/interviews/plan`.
   - *Is user authenticated?*
     - Yes -> Save session to DB. Redirect to `/interviews/[id]/execute`.
     - No -> Store pending session in `localStorage`. Redirect to `/login?redirect=interview`.

## 3. Active Interview Flow (Adaptive Branching)
**Trigger**: User submits an answer.
1. **Submission**
   - *Is answer < 10 characters?*
     - Yes -> Client-side block. "Your answer is too short for the AI to evaluate."
     - No -> Proceed. Send to `/v1/interviews/[id]/answers`.
2. **AI Evaluation (Backend Response)**
   - *Does the response contain `follow_up_generated: true`?*
     - Yes -> The backend adaptive engine decided a follow-up is needed. The frontend must inject a new node into the active question list (e.g., "Question 1a").
     - No -> The backend cleared the question. Move to the next primary question.
3. **Completion**
   - *Are there any remaining unasked questions in the queue?*
     - Yes -> Load next question.
     - No -> Display "Generating Report..." overlay and poll `/v1/interviews/[id]/report`.
