# SpeakLift: UX Philosophy

## Guiding Principles
The SpeakLift UX is built around focus and flow. The interface should disappear, leaving only the user and their career goals. We take heavy inspiration from high-performance productivity tools (Linear, Cursor, Vercel) and blend it with the emotional resonance of premium consumer apps (Spotify, Apple).

### Information Hierarchy & User Attention
- **One primary action per screen**: The user should never have to guess what to do next. The "Start Interview" or "Review Report" button should be the undeniable focal point.
- **Progressive Disclosure**: Hide complex settings and advanced analytics behind secondary interactions. Keep the main view exceptionally clean.
- **Breathing Room**: Use generous whitespace. Content should feel curated, not crammed.

### Navigation Principles
- **Flat Architecture**: Keep the hierarchy shallow. Users should be able to reach any core feature (Dashboard, Interviews, Profile, Settings) within one click.
- **Command Palette First**: Introduce a `Cmd+K` / `Ctrl+K` command palette for rapid navigation, creating a sense of speed and power-user mastery.

### Micro-interactions & Animations
Animations should feel like physical laws apply to the interface—snappy, intentional, and smooth.
- **Spring Physics**: Use spring animations (via Framer Motion) rather than linear easing for layout changes, giving UI elements a tangible, grounded feel.
- **Hover States**: Interactive elements should respond immediately to hover with subtle scale changes or backdrop shifts, confirming interactivity before the click.
- **Transitions**: Page transitions should be seamless. No hard flashes of white.

### Feedback & State Management
- **Optimistic UI**: Assume success for low-risk actions (e.g., pinning a report, updating a profile). Update the UI instantly while the network request resolves in the background.
- **Loading States**: Avoid traditional spinning loaders where possible. Use beautifully designed **Skeleton Screens** that mirror the incoming content layout, reducing perceived wait times.
- **Error Handling**: Errors should never feel like the user's fault. Use inline, conversational error messages ("Oops, we lost connection. Trying again...") rather than harsh red alert boxes. Provide an immediate action to recover.

### Empty States
Empty states are not a lack of content; they are an opportunity to onboard.
- Never show a blank screen.
- If a user has no interviews, show a beautiful illustration with a clear, inspiring call-to-action ("Let's conquer your first interview").

### Accessibility
A premium product is inherently accessible.
- **Keyboard Navigation**: The entire app must be navigable via Tab and Enter. 
- **Focus Rings**: Implement beautiful, intentional focus rings that match the brand identity, never relying on default browser outlines.
- **Contrast**: Ensure WCAG AA compliance, especially in Dark Mode, maintaining legibility without sacrificing aesthetic depth.

### Keyboard Shortcuts
Power users expect speed.
- `Cmd + K`: Open Command Palette
- `Cmd + Enter`: Submit Answer
- `Space`: Toggle play/pause on audio feedback
- Esc to close modals instantly.
