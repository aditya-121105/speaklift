# SpeakLift: Typography System

Typography is the absolute foundation of the SpeakLift interface. The layout, hierarchy, and emotional resonance of the product are dictated almost entirely by text, not borders or backgrounds.

## 1. Font Family
- **Primary Interface Font**: `Inter` or `Geist`. 
  - *Why*: These are modern, geometric, neo-grotesque sans-serifs designed specifically for high legibility on computer screens. They offer exceptional clarity in dense data interfaces (like analytics dashboards).
- **Code/Monospace Font**: `Geist Mono` or `JetBrains Mono`.
  - *Why*: For displaying code snippets within candidate answers or AI technical feedback, a premium, readable monospace font is required.

## 2. Typography Scale
We utilize a fluid, proportional scale based on Tailwind's default configuration, but with tighter line heights for headings.

### Display Typography
- Used for massive impact (e.g., the Readiness Score number, Hero section headlines).
- **Scale**: `text-5xl` to `text-7xl`.
- **Styling**: `font-bold tracking-tighter leading-none`. The negative letter spacing (`tracking-tighter`) prevents massive text from feeling loose and disconnected.

### Headings
- Used for section titles (e.g., "Interview Report", "Skill Breakdown").
- **Scale**: `text-xl` to `text-4xl`.
- **Styling**: `font-semibold tracking-tight leading-tight`.

### Body
- Used for the bulk of the content (AI feedback, user answers, descriptions).
- **Scale**: `text-base` (16px) is the standard for long-form reading. `text-sm` (14px) is the standard for UI elements (cards, lists).
- **Styling**: `font-normal leading-relaxed` for reading, `leading-snug` for UI components.

### Caption & Muted
- Used for timestamps, subtle metadata, and secondary labels.
- **Scale**: `text-xs`.
- **Styling**: `font-medium text-text-muted uppercase tracking-wider` (when used as a tiny eyebrow label) or standard lowercase for simple timestamps.

## 3. Weight System
- **Regular (400)**: Standard body copy.
- **Medium (500)**: Buttons, Navigation Links, Tab titles, and UI labels. It provides just enough punch to stand out from body text without commanding the attention of a heading.
- **Semi-Bold (600)**: Standard headings and emphasized data points.
- **Bold (700)**: Reserved for Display text.

## 4. Numeric Typography (Tabular Nums)
When displaying statistics, Readiness Scores, or any vertical lists of numbers, use `tabular-nums`. This ensures that all numbers are rendered at a uniform width, preventing the UI from jittering when numbers tick up or down during animations.

## 5. Line Height (Leading)
- **Headings**: The larger the text, the tighter the line height. A `text-5xl` heading should have a line height of `1` (`leading-none`).
- **Body Text**: Long-form AI feedback requires breathing room to reduce cognitive load. Use `leading-relaxed` (1.625) for these blocks.

## 6. Button Text
Buttons must never use full uppercase (`UPPERCASE`) text unless they are microscopic eyebrow labels. Full uppercase is a remnant of Material Design 1.0 and feels dated. Use sentence case or title case with `font-medium`.
