# SpeakLift: Spacing System

Spacing is the primary architectural tool for grouping information. If spacing is inconsistent, the interface feels fragile. SpeakLift strictly adheres to a **4pt Grid System**, enforced natively by Tailwind CSS.

## The Whitespace Philosophy
Whitespace is not empty space; it is an active design element. 
- Do not fear empty space. Resist the urge to fill the screen with unnecessary widgets.
- Generous spacing around a component elevates its perceived importance.

## 1. The 4pt Grid
Every margin, padding, height, and width dimension in the application must be a multiple of 4 pixels (e.g., 4, 8, 12, 16, 24, 32, 48, 64).
- Magic numbers (e.g., 17px, 23px) are strictly forbidden as they break the rhythmic flow of the UI.

## 2. Micro Spacing (4px - 8px)
- **Tailwind Tokens**: `gap-1`, `gap-2`, `p-1`, `p-2`.
- **Usage**: Tightly coupled elements.
  - Spacing between an icon and its text label in a button.
  - Spacing between a tiny caption and its parent heading.

## 3. Component Spacing (16px - 24px)
- **Tailwind Tokens**: `p-4`, `p-6`, `gap-4`, `gap-6`.
- **Usage**: Internal padding for cards, modals, and list items.
  - A standard AI Insight Card receives `p-6` (24px) to ensure the text does not feel claustrophobic against the border.
  - Spacing between inputs in a form.

## 4. Section Spacing (32px - 64px)
- **Tailwind Tokens**: `gap-8`, `gap-12`, `mb-16`.
- **Usage**: Separating major logical blocks on a page.
  - The gap between the Hero section and the "Recent Interviews" grid.
  - The spacing between distinct sections inside an Interview Report.

## 5. Layout Containers
- **Max Width**: The application uses a constrained max-width (`max-w-7xl` or `1280px`) for standard dashboards. On ultra-wide monitors, the content remains centered, preventing lines of text from becoming unreadably long.
- **Reading Width**: For long-form text (like AI feedback), constrain the width further to `max-w-prose` (approx 65 characters per line). This is the scientifically optimal width for human reading speed.

## 6. Responsive Spacing
Spacing must scale down gracefully on mobile devices.
- Desktop might use `p-8` (32px) for card padding, but on mobile, that wastes precious real estate. 
- **Rule**: Use Tailwind's responsive modifiers to collapse spacing on smaller screens (e.g., `p-4 md:p-8`).
