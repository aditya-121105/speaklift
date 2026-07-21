# SpeakLift: User Flows

This document outlines the step-by-step paths users take to achieve specific goals within SpeakLift.

## 1. First-Time Onboarding
- **Goal**: Reach the "Aha!" moment (first AI interaction or mock interview) in under 5 minutes.
- **Flow**: Landing Page -> Click "Get Started" -> Sign Up (Email/OAuth) -> Welcome Splash -> "Upload Resume" or "Skip for Now" -> Target Job Role Input -> AI generated personalized welcome & Dashboard generation.

## 2. Returning User (Daily Practice)
- **Goal**: Immediate re-engagement with minimal friction.
- **Flow**: Login -> Dashboard -> View "Today's AI Insight" & Readiness Score -> Click Primary CTA ("Start Recommended Practice") -> Complete short mock session -> Review feedback -> Return to Dashboard.

## 3. Company-Specific Preparation
- **Goal**: Tailor practice for a specific upcoming interview.
- **Flow**: Dashboard -> "New Interview" -> Paste Job Description (JD) -> System extracts skills -> Select target company -> Start tailored mock interview -> Receive specialized report.

## 4. Mock Interview Execution
- **Goal**: High-focus simulated interview environment.
- **Flow**: Pre-interview Check (Audio/Mic permissions, future) -> "Start" -> Question 1 displayed -> User inputs answer -> Submit -> "AI Thinking" state -> Follow-up generated based on answer -> User inputs answer -> Submit -> Move to Question 2 -> (Repeat) -> "End Interview" -> Redirect to Report Generation loading state.

## 5. Report Review
- **Goal**: Digest feedback constructively and view progress.
- **Flow**: Interview Completion -> Report Splash Screen (Score + AI Praise) -> Detailed Breakdown (Question by Question) -> Recommendations & Weaknesses -> Click "Add to Learning Roadmap" -> Return to Dashboard.

## 6. Profile Management
- **Goal**: Update the underlying AI context.
- **Flow**: Sidebar -> "Profile" -> View current parsed resume skills -> Upload new resume -> System confirms updates -> New AI context established.

## 7. Error Recovery (Authentication)
- **Goal**: Graceful degradation when session expires.
- **Flow**: User clicks action -> API returns 401 Unauthorized -> Interceptor catches error -> Global state cleared -> User redirected to Login with param `?expired=true` -> Toast message: "Session expired, please log in again" -> User logs in -> Redirected back to the interrupted action.
