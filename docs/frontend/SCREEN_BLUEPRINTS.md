# SpeakLift: Screen Blueprints

This document defines the structural layout and hierarchy of the primary screens.

## 1. Dashboard Blueprint
- **Layout**: Sidebar (Left, 240px) + Main Content Area.
- **Header**: User Profile Dropdown (Top Right).
- **Hero Section**: 
  - Greeting text (text-3xl).
  - AI Insight Card spanning 100% width of the container.
- **Main Grid**: 2 columns on desktop, 1 on mobile.
  - *Left Column (70%)*: 
    - Readiness Score Widget (prominent circular dial).
    - Skill Progression Line Chart.
  - *Right Column (30%)*:
    - "Start Practice" Action Card.
    - Mini Learning Roadmap (3 bullet points).
- **Below the Fold**: Recent Interviews Table (Full width).
- **Responsive Priority**: On mobile, stack Readiness Score -> Action Card -> AI Insight.

## 2. Active Interview Blueprint
- **Layout**: Focused view. No Sidebar. No Header navigation.
- **Header**: Simple "Leave Interview" ghost button (Top Left). Current Question counter "Question 2 of 5" (Top Center).
- **Main Content** (Constrained to `max-w-3xl` for readability):
  - *Top*: The Interview Question text (large, legible serif or clean sans).
  - *Middle*: The AI Anchor. If it's a follow-up, the AI Spark sits next to the text.
  - *Bottom*: A massive `<textarea>` (or audio visualizer in the future) taking up 50% of the viewport height.
- **Sticky Footer**:
  - "Submit Answer" button (Bottom Right).
  - "Skip" button (Bottom Left).
- **Responsive Priority**: The textarea must remain entirely visible above the mobile software keyboard.

## 3. Interview Report Blueprint
- **Layout**: Sidebar + Main Content.
- **Header**: Breadcrumbs (`Interviews > Report`).
- **Hero Grid**: 
  - Large overall score (e.g., "85/100").
  - 3 mini stat cards (Vocabulary Richness, Confidence, Grammar).
- **AI Executive Summary**: A full-width card containing the qualitative AI feedback ("Strengths", "Weaknesses", "Communication Tone").
- **Question Breakdown (Accordion or List)**:
  - For each question: Shows the question, the user's answer, and specific AI feedback.
  - *Design*: The user's answer is styled like a standard message bubble. The AI's feedback is styled with a subtle `--ai-accent` border to differentiate.
- **Responsive Priority**: The executive summary remains at the top. The mini stat cards wrap into a 2x2 grid on mobile.

## 4. Onboarding Blueprint
- **Layout**: Centered Modal over a blurred background.
- **Header**: Minimal logo.
- **Content**: 
  - A dynamic multi-step wizard (`Step 1 of 2`).
  - Cross-fading transitions between steps.
- **Footer**: Progress bar indicating how close they are to completion.
