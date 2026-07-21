# SpeakLift: Motion System

Motion in SpeakLift serves three purposes: to clarify relationships, to obscure latency, and to delight the user. Animations must never cause motion sickness or make the app feel sluggish.

## 1. Timing Tokens
- **Instant (0ms)**: For critical, high-frequency actions where any delay is annoying (e.g., typing in an input field).
- **Snappy (150ms)**: For micro-interactions (e.g., button hovers, checkbox toggles).
- **Fluid (300ms)**: For layout changes (e.g., opening a modal, expanding an accordion).
- **Stately (500ms+)**: Reserved for major page transitions or the final reveal of a calculated score.

## 2. Easing Curves
Linear animations look robotic. We use bespoke easing curves to mimic physical mass.
- **Tailwind `ease-out`**: The default for entrances (starts fast, slows down at the end).
- **Framer Motion Springs**: Used for layout changes. A spring with a slight bounce (e.g., `stiffness: 300, damping: 30`) makes elements feel physical and satisfying to interact with.

## 3. Hover Animations
- Buttons and cards should react immediately to hover.
- Rather than violently shifting position, they should gently scale up (`scale: 1.02`) or shift their background color luminance smoothly over 150ms.

## 4. Page Transitions
- When navigating between major dashboard sections, avoid harsh white flashes.
- Use a very subtle fade and a tiny upward translation (`opacity: 0 -> 1, y: 10 -> 0`). This gives the sensation that new content is sliding into view from below, maintaining spatial continuity.

## 5. Loading Animations
- **Skeletons over Spinners**: A spinner says "Please wait." A skeleton says "The data is already arriving."
- Skeletons should use a soft, sweeping gradient animation (shimmer) rather than a harsh blinking pulse.

## 6. Counter Animations
- When a user finishes an interview and the Readiness Score is calculated, the number should not just appear.
- It should tick up dynamically from 0 to the final score over 1.5 seconds. This builds anticipation and gamifies the result.

## 7. The AI Streaming Effect
- When the AI generates feedback, the text must stream in as if being typed.
- This obscures backend latency and makes the AI feel like an active participant.
- The typing speed should be very fast—faster than human typing, but slow enough to perceive the generation (approx. 20-30 characters per second).

## 8. Reduce Motion Support
- Accessibility is paramount. If a user has `prefers-reduced-motion: reduce` configured at the OS level, all Framer Motion and Tailwind animations must gracefully degrade to instant state changes. We never force animation on a user who has explicitly opted out.
