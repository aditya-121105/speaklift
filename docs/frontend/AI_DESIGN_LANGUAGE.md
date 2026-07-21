# SpeakLift: AI Design Language

The AI is the core product of SpeakLift. Its presence in the UI must be distinct, instantly recognizable, and emotionally resonant.

## 1. The Visual Anchor: The Spark
Whenever the AI speaks, acts, or thinks, it is represented by a specific visual anchor—"The Spark."
- **Idle State**: A small, geometric icon (e.g., a stylized four-point star or a sleek circle) rendered in the `--ai-accent` color.
- **Thinking State**: The Spark transforms into a morphing, blurred mesh gradient that slowly rotates. This visually communicates complex computation without using a frustrating loading spinner.
- **Success State**: The Spark emits a subtle, momentary outward ripple (pulse) when delivering high praise.

## 2. AI Insight Cards
When the AI provides proactive advice on the Dashboard or in a Report:
- **Styling**: The card uses a very subtle `--ai-accent` background fill at 2% opacity. The border has a faint gradient. This visually separates AI-generated insights from standard user data.
- **Typography**: The AI's voice uses a slightly different font weight or a highly legible serif (optional) to differentiate its "voice" from the system's "UI text."

## 3. Streaming Responses
The illusion of an active conversation is critical.
- When an AI evaluation is generated, the text must never appear all at once in a massive block.
- It streams into the UI rapidly (character by character or word by word).
- As it streams, a subtle glowing cursor leads the text.

## 4. Recommendations & Action Cards
The AI doesn't just talk; it creates actionable items.
- If the AI suggests, "You should practice System Design," that text must be accompanied by an interactive Action Card directly below it.
- **Action Card**: A small, highly clickable widget that allows the user to instantly launch the suggested practice session with one click. The AI bridges the gap between insight and action.

## 5. Voice Interactions (Future-Proofing)
While v1 is text-based, the UI framework for the AI must support voice.
- The "Spark" will eventually double as an audio visualizer, reacting to the frequencies of the candidate's voice and the AI's synthesized responses.
- The central AI container is designed to float in the center of the screen during a live audio session, pulsing in tandem with the conversation.
