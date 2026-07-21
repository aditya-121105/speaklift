# SpeakLift: Color System

The SpeakLift color system is designed to be timeless, drawing inspiration from high-end productivity software rather than gaming or pure enterprise applications.

## Dark Mode Philosophy
SpeakLift is inherently a Dark Mode-first application, catering to students and professionals working late into the night. 
- **No True Blacks**: We do not use `#000000` for backgrounds. True black creates harsh contrast lines that cause eye strain.
- **Deep Slates**: The base `--background` should be a deep, rich slate (`#0A0A0A` or `#111111`).
- **Desaturated Semantics**: In light mode, a bright Emerald Green works well. In dark mode, that same bright green vibrates against the dark background. Semantic colors must be desaturated and lightened slightly in dark mode to maintain readability and calmness.

## Layered Surfaces
Color is our primary tool for defining depth without relying on heavy shadows.
- **Base Level (`--background`)**: The canvas.
- **Level 1 (`--surface`)**: Cards and panels. Slightly lighter than the background in dark mode, or pure white (`#FFFFFF`) in light mode over a soft gray background (`#F9FAFB`).
- **Level 2 (`--surface-elevated`)**: Used for dropdowns, popovers, and sticky navigation. It is the lightest gray in dark mode to signify proximity to the user.

## Accent Strategy
The brand relies on reduction. Color is only used to draw attention or indicate state.
- If everything is colored, nothing stands out.
- The default state of buttons, borders, and icons should be grayscale.
- Only the **Primary Action** on a screen (e.g., "Start Interview") should receive the `--primary` background fill.

## Glass Usage & Gradients
- **Glassmorphism**: We use translucent background colors (`bg-background/80 backdrop-blur-md`) for sticky headers and command palettes. This creates a premium, native-app feel.
- **Gradients**: Linear and radial gradients are reserved almost exclusively for the **AI Identity**. A soft mesh gradient in the background of the hero section or inside an AI Insight card signifies that the intelligence engine is present.

## Hover & Focus Colors
- **Hover**: Should represent a subtle shift in luminance. We prefer lightening dark elements and darkening light elements on hover.
- **Focus**: Accessibility is non-negotiable. The `--border-focus` color must contrast sharply against the background to guarantee keyboard navigators always know where they are.

## Charts
Data visualization (Recharts) requires its own palette.
- Do not use the standard `--primary` for a line chart, as it may clash with semantic UI elements.
- Use a dedicated array of muted, harmonious colors (e.g., Soft Teal, Muted Indigo, Slate) for multi-line charts, ensuring color blindness accessibility (avoiding red-green adjacent reliance).
