# SpeakLift: Design Tokens

## The Philosophy of Semantic Tokens
SpeakLift utilizes **semantic design tokens** rather than raw color values. A semantic token defines *how* a color is used rather than *what* the color is. For example, using `--surface-elevated` is significantly more scalable than using `--gray-800`. 

Semantic tokens provide three immense benefits:
1. **Flawless Theming**: Dark mode simply involves redefining the semantic token values at the root scope. Components never need hard-coded `dark:` modifiers for colors.
2. **Consistency**: Engineers do not have to guess which shade of gray to use for a border. They simply use the `--border` token.
3. **Future-Proofing**: If the brand identity shifts from blue to purple, we change the `--primary` token, and the entire application updates instantly without a massive find-and-replace operation.

## Semantic Token Dictionary

### Core Backgrounds
- **Background** (`--background`): The deepest layer of the application. The primary canvas.
- **Surface** (`--surface`): The standard container background (e.g., standard cards).
- **Surface Elevated** (`--surface-elevated`): Containers that float above the surface (e.g., dropdowns, modals, floating action bars).

### Borders & Separators
- **Border** (`--border`): The default subtle separator used for cards, dividers, and input borders.
- **Border Focus** (`--border-focus`): The intense ring color used when an element receives keyboard focus.

### Interactive Primary
- **Primary** (`--primary`): The main brand accent. Used for primary CTAs and major highlights.
- **Primary Hover** (`--primary-hover`): A slightly darker (or lighter in dark mode) variant for hover interactions.
- **Primary Active** (`--primary-active`): A deeper variant for the depressed button state.
- **Primary Soft** (`--primary-soft`): A highly transparent version of primary (e.g., `8%` opacity) used as a background for primary text or active navigation links.

### The AI Identity
- **AI Accent** (`--ai-accent`): A distinct, vibrant color (e.g., Iris Blue or Violet) reserved *exclusively* for AI-driven elements (insights, recommendations, generating states).

### Typography
- **Text Primary** (`--text-primary`): The highest contrast text. Used for headings and vital data.
- **Text Secondary** (`--text-secondary`): Slightly muted text. Used for body copy and descriptions.
- **Text Muted** (`--text-muted`): Highly muted text. Used for placeholders, secondary timestamps, and disabled states.
- **Text Inverted** (`--text-inverted`): Text designed to sit on top of the `--primary` background.

### Semantic Feedback
- **Success** (`--success`): Represents positive reinforcement, high scores, and completed tasks.
- **Warning** (`--warning`): Represents caution, medium scores, or non-critical suggestions.
- **Danger** (`--danger`): Represents critical errors, destructive actions (e.g., "Delete Account"), or very low scores.
- **Info** (`--info`): Represents neutral, objective system information.
