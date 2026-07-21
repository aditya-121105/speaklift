# SpeakLift: Onboarding Flow

The goal of onboarding is to reach "First Value" (the first AI interaction or mock interview) in under 3-5 minutes without feeling overwhelming.

## 1. The Welcome Screen
- **Visuals**: A clean, centered modal over a blurred dashboard background.
- **Copy**: "Welcome to SpeakLift. Let's configure your AI coach."

## 2. Step 1: The Resume (High Value, High Friction)
- **Concept**: We want their resume, but we must not force it if they are on mobile or don't have it ready.
- **UI**: A large, dashed drag-and-drop zone.
- **Actions**:
  - `Primary`: "Upload PDF/DOCX"
  - `Secondary (Ghost)`: "Skip for now, I'll do this later."
- **If Uploaded**: Show a highly satisfying parsing animation. Extract 3-4 key skills and display them: "We see you're strong in Python and React." This proves the AI works immediately.

## 3. Step 2: The Target (Low Friction)
- **Concept**: We need to know what they are preparing for to personalize the dashboard.
- **UI**: Two simple inputs.
  - "Target Job Title" (e.g., Software Engineer)
  - "Target Company (Optional)" (e.g., Google)
- **Actions**: `Primary`: "Set Target"

## 4. The Handoff (Reaching Value)
- The modal dismisses via a smooth scale-down animation.
- The Dashboard is revealed.
- The AI "Spark" animates in the center of the hero section.
- Text streams in: *"Hello. I've reviewed your profile. Based on your target of Software Engineer, I recommend starting with a 3-question baseline technical interview. Are you ready?"*
- A massive primary button pulses: **"Start Baseline Interview"**.

## Time to Value
By allowing the resume skip and keeping inputs minimal, a user can go from account creation to their first mock interview in approximately 45 seconds.
