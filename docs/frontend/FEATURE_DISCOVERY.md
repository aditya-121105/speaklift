# SpeakLift: Feature Discovery

To avoid overwhelming new users, advanced features are hidden initially and progressively revealed as the user demonstrates mastery of the core loop.

## 1. The Core Loop (Days 1-3)
- **Visible Features**: Dashboard, Start Interview, Basic Report Review.
- **Hidden Features**: Command Palette (`Cmd+K`), Advanced Analytics (Lexical density, Hedging phrases), Custom Job Description inputs.

## 2. Progressive Disclosure Triggers

### Trigger: Completing 3 Interviews
- **Discovery Action**: A subtle toast or a special AI Insight Card appears on the dashboard.
- **Message**: "You're getting the hang of this. Want to see how you perform against a specific job? Try pasting a Job Description."
- **Result**: The "New Interview" flow now highlights the JD paste box, which was previously minimized or hidden.

### Trigger: Navigating via Mouse heavily
- **Discovery Action**: An inline tooltip appears near the search icon.
- **Message**: "Pro tip: Press `Cmd+K` anywhere to quickly jump between pages or start an interview."
- **Result**: Introduces power-user keyboard shortcuts.

### Trigger: Consistently scoring >80% on Technical, but <60% on Communication
- **Discovery Action**: The AI modifies the Report view.
- **Result**: It unlocks and automatically expands the "Advanced Communication Analytics" panel (which usually requires a click to expand), highlighting exactly *why* their score is suffering (e.g., filler words, run-on sentences).

## 3. The "New Feature" Badge
When shipping a completely new feature (e.g., Voice Interviews):
- Do not use aggressive modal popups that block the user upon login.
- Add a subtle, pulsating primary-colored dot next to the relevant sidebar item.
- The AI's daily insight can gently mention the feature: "I've just learned how to conduct audio interviews. Want to try it today?"
