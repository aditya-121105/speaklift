# SpeakLift: Screen Inventory

This document catalogs every major screen required for v1, defining their objective, entry/exit points, and key interactive elements.

## 1. Dashboard (`/dashboard`)
- **Purpose**: Provide immediate situational awareness and the next best action.
- **Target User**: All authenticated users.
- **Entry Points**: Login, Logo click.
- **Exit Points**: New Interview, Profile, Report Review.
- **Primary CTA**: "Start Recommended Practice" (based on AI roadmap).
- **Secondary CTA**: "Upload New JD".
- **AI Presence**: High. The "Today's Insight" card greets them.
- **Empty State**: "Welcome to SpeakLift. Let's set up your profile to generate your first roadmap."

## 2. Interview Setup (`/interviews/new`)
- **Purpose**: Configure the parameters of a mock session.
- **Target User**: User preparing for a specific role.
- **Primary CTA**: "Start Interview".
- **Loading State**: "Analyzing Job Description..." (skeleton loader mimicking the extracted skill tags).
- **Error State**: "We couldn't process this text. Try pasting just the requirements section."

## 3. Active Interview (`/interviews/[id]/execute`)
- **Purpose**: A distraction-free zone for answering questions.
- **Target User**: User actively practicing.
- **Entry Points**: Interview Setup.
- **Exit Points**: "End Interview" (triggers submission).
- **Primary CTA**: "Submit Answer".
- **Secondary CTA**: "Skip Question".
- **AI Presence**: The AI "Spark" pulses while waiting for the user to answer, and morphs into a "Thinking" state after submission before presenting follow-ups.

## 4. Interview Report (`/interviews/[id]/report`)
- **Purpose**: Deliver complex qualitative and quantitative feedback.
- **Primary CTA**: "Review Next Steps".
- **Secondary CTA**: "Retake Interview".
- **Progress Indicators**: Overall Score, Concept Coverage %, Confidence %.
- **Success Criteria**: User understands *why* they received their score and *what* to do about it.

## 5. Profile Management (`/profile`)
- **Purpose**: Maintain the user's ground truth data (Resume, Target Role).
- **Primary CTA**: "Save Changes".
- **Empty State**: (For Resume) "Upload your resume so the AI can tailor questions to your experience."

## 6. Authentication (`/login`, `/register`)
- **Purpose**: Secure access.
- **Primary CTA**: "Sign In" / "Create Account".
- **Error State**: Inline red text below fields: "Invalid credentials."
