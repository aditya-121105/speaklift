# SpeakLift: Visual Identity

The visual identity of SpeakLift aims to bridge the gap between rigorous technical preparation and consumer-grade emotional design. It should feel like a high-end tool built for professionals, yet accessible to ambitious students.

## Brand Personality
- **Tone**: Encouraging, precise, intelligent, and calm.
- **Vibe**: A quiet, well-lit modern library meets a high-tech command center.

## Typography Philosophy
Typography is the loudest voice in our UI.
- **Primary Typeface**: `Inter` or `Geist`. We require a highly legible, geometrically precise sans-serif that looks stunning in dense data interfaces.
- **Display Typeface**: For marketing headers or massive dashboard numbers, use a slightly tighter, heavier weight (e.g., `Inter Tight` or `Cal Sans`) to provide punch.
- **Hierarchy**: Rely on weight and color contrast (not just size) to establish hierarchy. Muted grays for secondary text are critical for reducing cognitive load.

## Color Philosophy
- **Base**: A monochromatic scale of grays with subtle blue/slate undertones. It should never feel like pure, harsh #000000 or #FFFFFF.
- **Primary Accent**: An electric, optimistic color (e.g., a vibrant Iris Blue or Violet). Used sparingly. Only the most critical path (Primary Buttons, AI highlights) gets this color.
- **Semantic Colors**: Emerald Green for success/strengths, Amber for warnings/suggestions, Rose for errors. These must be muted and pastel in Dark Mode to prevent eye strain.

## Dark Mode Philosophy
SpeakLift is an app users might stare at late into the night before an interview.
- **Dark Mode First**: The design should be conceived in Dark Mode and translated to Light Mode.
- **True Blacks vs. Slates**: Avoid `#000000` backgrounds. Use deep slates (e.g., `#0A0A0A` or `#111111`) to soften the contrast and allow for elevation layers.

## Elevation Philosophy
We do not use heavy drop shadows. 
- **Light Mode**: Use very subtle, diffused, and low-opacity shadows with large blur radiuses.
- **Dark Mode**: Shadows don't work in the dark. Instead, use thin, 1px semi-transparent borders (`rgba(255,255,255,0.1)`) and slightly lighter background fills to indicate elevation.

## Glass & Gradient Usage
- **Glassmorphism**: Use it strategically, not everywhere. A blurred, translucent navigation bar or a sticky AI command palette creates a sense of depth and modernity.
- **Gradients**: Avoid harsh, linear gradients on large surfaces. Use soft, radial, mesh gradients to represent the "AI thinking" state or to subtly illuminate the background of the hero section.

## Motion Philosophy
- **Snappy & Restrained**: 200-300ms durations. Easing curves should start fast and end slow (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Staggered Exits/Entrances**: When loading lists (e.g., Interview Reports), stagger their entrance slightly to guide the eye.

## Illustration & Icon Philosophy
- **Icons**: Use a consistent, geometric icon set (e.g., Lucide or Phosphor). Keep them a consistent weight (usually 1.5px or 2px).
- **Illustrations**: Avoid the "Corporate Memphis" style (flat, abstract people with blue skin). If using illustrations, lean towards abstract 3D geometry (glass spheres, metallic shapes) or minimalist wireframe art. It feels more futuristic and mature.

## AI Visual Identity
The AI needs a visual anchor.
- **The Spark**: Represent the AI using a subtle glowing spark, a morphing mesh gradient circle, or a unique icon. 
- **Text Generation**: When the AI generates a report, text should stream in smoothly. Text should perhaps carry a subtle shimmer effect upon rendering to signify it was freshly minted by the engine.
