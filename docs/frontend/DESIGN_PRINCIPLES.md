# SpeakLift: Design Principles

## Core Directives

1. **Minimal, yet powerful.**
   The UI should get out of the way. If a visual element does not convey meaning or aid navigation, remove it. Use reduction as a design tool.
   
2. **Intelligent and Context-Aware.**
   The UI should feel like it anticipates the user's needs. If an interview is scheduled for tomorrow, that should be the hero element. The platform should feel alive.

3. **Dynamic.**
   Interfaces that react smoothly to user input feel higher quality. Content should slide into place, numbers should tick up smoothly, and charts should animate.

4. **Human.**
   Despite being an AI tool, the platform must feel deeply empathetic. The language used in the UI should be encouraging and coaching, not robotic or clinical.

5. **Never Flashy.**
   Avoid aggressive neobrutalism or hyper-saturated web3 aesthetics. The design must inspire trust and professionalism.

6. **Never Childish.**
   Avoid oversized bubbly icons, primary colors, or gamification that treats the user like a child. These are young adults preparing for serious careers. 

7. **Never Corporate.**
   Avoid the sterile, dry aesthetic of enterprise HR software (Workday, traditional LMS). SpeakLift is a consumer product.

---

## Gamification Philosophy: Tasteful Motivation

We want to build habits without being manipulative. Motivation should feel like an elite sports tracker (e.g., Strava, Apple Fitness) rather than a mobile game.

- **Streaks**: Track consecutive days of practice. Keep the UI representation subtle—a small flame or glowing dot—rather than an intrusive popup.
- **Skill Levels**: Visualize progress from "Novice" to "Expert" using elegant tiered progress bars or radar charts for specific competencies (e.g., Python, System Design, Communication).
- **Weekly Goals**: Let users set intentional targets (e.g., "Complete 2 interviews this week"). Celebrate gently when achieved.
- **Improvement Graphs**: Show beautiful, smoothed line charts charting their Confidence Score or Readiness Score over time. Seeing the line go up is the ultimate motivator.
- **Confidence Indicators**: Instead of arbitrary points, use meaningful metrics. "You are in the top 10% of candidates for React roles based on your recent answers."

---

## Mobile Philosophy

SpeakLift must be flawless on mobile, recognizing that Gen Z users will often review feedback or do quick practice rounds on their phones.

### Responsive Behavior
- **Desktop**: Expansive, multi-column layouts optimizing data density (e.g., showing the question, the answer, and the AI feedback side-by-side).
- **Tablet**: A hybrid approach. Utilize split-views and slide-over panels for reading reports.
- **Mobile**: Single-column focus. The UI must ruthlessly prioritize what matters right now.

### Touch Interactions
- **Tap Targets**: Minimum 44x44pt for all interactive elements. No accidental mis-taps.
- **Swipe Gestures**: Use native-feeling gestures. Swipe right to go back, swipe left to dismiss a notification, swipe up to reveal an AI insight panel.
- **Bottom Navigation**: Keep primary actions within thumb reach. Avoid forcing the user to reach the top of tall phone screens.
- **Haptics**: When deployed as a PWA or wrapped app, use subtle haptic feedback for success states or when achieving a streak.
