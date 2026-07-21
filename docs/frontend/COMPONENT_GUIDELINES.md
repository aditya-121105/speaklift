# SpeakLift: Component Guidelines

These rules dictate how atomic components behave and combine, ensuring visual consistency across all features.

## 1. Buttons
- **Primary**: Used once per screen for the main action (e.g., "Start Interview"). Filled with `--primary`, white text.
- **Secondary**: Used for alternative actions. Transparent background, `--border` outline, `--text-primary` text.
- **Ghost**: Used for low-priority actions (e.g., "Cancel", "Skip"). No background, no border, subtle hover effect.
- **Destructive**: Used for dangerous actions (e.g., "Delete Account"). Filled with `--danger`. Always requires a confirmation dialog.
- **Loading State**: A primary button clicked during a network request must not freeze. It transitions to a disabled state with a subtle inline loading spinner replacing its icon, maintaining its exact width to prevent layout shift.

## 2. Inputs & Forms
- **Borders**: Thin, subtle gray borders (`--border`).
- **Focus**: When an input is focused, it receives a thick, vibrant ring (`--border-focus`) to clearly indicate the active element.
- **Validation**: Inline errors appear instantly below the input in `--danger` text. The input border also turns red.
- **Labels**: Always use visible labels. Placeholders are not a replacement for labels.

## 3. Cards
- **Usage**: The primary container for distinct pieces of information (e.g., an Interview Session summary).
- **Styling**: `bg-surface`, `border border-border`, `rounded-xl`. 
- **Hover**: If a card is clickable (acting as a link), it should gently translate upward (`-translate-y-1`) and increase border luminance on hover.

## 4. Dialogs & Modals
- **Backdrop**: A blurred, dark overlay (`bg-background/80 backdrop-blur-sm`) to entirely obscure the background and force focus on the modal.
- **Width**: Constrained (`max-w-md` or `max-w-lg`) to prevent text from stretching uncomfortably.
- **Dismissal**: Must be dismissible by clicking the backdrop or pressing the `Esc` key.

## 5. Navigation
- **Sidebar**: The primary navigation for the desktop dashboard. Collapses to a thin icon-only strip or disappears into a Hamburger menu on mobile.
- **Top Bar**: Used for global context—Breadcrumbs, the User Profile dropdown, and the Command Palette trigger (`Cmd+K`).

## 6. Empty States
- Never show a blank screen or an empty table grid.
- Always center a subtle, abstract illustration or icon.
- Provide a clear, encouraging headline ("No interviews yet").
- Provide a Primary Button to immediately remedy the empty state ("Start your first practice").

## 7. Toasts / Notifications
- **Usage**: For transient, non-blocking feedback (e.g., "Profile updated successfully").
- **Placement**: Bottom-right on desktop, Top-center on mobile.
- **Auto-dismiss**: 3-5 seconds.
- **Actionable**: If an action is reversible (e.g., "Report deleted"), include an "Undo" button directly inside the toast.

## 8. Skeletons
- Used during data fetching.
- Must mirror the exact layout of the expected content. If a card has an avatar and three lines of text, the skeleton must have a circle and three rounded rectangles.

## 9. Charts
- Utilize Recharts with custom tooltips.
- Do not use default axis lines; they clutter the UI. Hide the Y-axis line entirely and use very faint, dashed horizontal grid lines (`--border`) for reference.
- Use a smooth bezier curve (`type="monotone"`) for line charts, not sharp jagged lines, to make progress feel organic.
