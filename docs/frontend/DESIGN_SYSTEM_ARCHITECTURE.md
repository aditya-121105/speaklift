# SpeakLift: Design System Architecture

SpeakLift utilizes Tailwind CSS configured deeply to match our specific visual identity. We do not use default Tailwind colors out of the box; they are mapped to semantic CSS variables to ensure flawless Dark Mode transitions.

## 1. Token Architecture (CSS Variables)
All colors are defined as HSL values in `globals.css` and mapped in `tailwind.config.ts`.

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --primary: 252 100% 64%; /* SpeakLift Iris */
    --primary-foreground: 0 0% 100%;
    /* Semantic Colors */
    --success: 142 71% 45%;
    --warning: 38 92% 50%;
    --destructive: 0 84% 60%;
  }
  .dark {
    --background: 0 0% 3.9%; /* Deep Slate, not true black */
    --foreground: 0 0% 98%;
    /* Dark mode requires desaturated semantic colors to reduce eye strain */
    --success: 142 60% 40%;
  }
}
```

## 2. Spacing Scale
We strictly adhere to the 4pt grid system provided by Tailwind.
- **Micro**: `gap-1`, `gap-2` (4px, 8px) for tightly coupled items (icon + text).
- **Component**: `p-4`, `p-6` (16px, 24px) for card padding.
- **Layout**: `gap-8`, `gap-12` (32px, 48px) for section separation.

## 3. Border Radius
SpeakLift leans towards modern, smooth geometry.
- Buttons, Inputs, Cards: `rounded-xl` or `rounded-2xl`.
- Avoid sharp `rounded-none` or fully pill-shaped `rounded-full` for standard containers, as they look either too corporate or too childish.

## 4. Typography Scale
Configured in `tailwind.config.ts` using the `Inter` typeface.
- Use `tracking-tight` for large headers (`text-4xl` and above) to give them a premium, editorial feel.
- Use `leading-relaxed` for long-form AI reports to maximize readability.

## 5. Elevation & Borders
- **Light Mode**: Utilize very soft, large-radius shadows (`shadow-sm`, `shadow-md` modified in config to have a lower opacity like 4%).
- **Dark Mode**: Shadows are essentially invisible. Instead, we use `border border-white/10` to define edges and `bg-white/5` for elevated cards.

## 6. Animation Timing
Animations use Framer Motion or Tailwind transitions.
- **Micro-interactions (Hover, Active)**: `duration-150` or `duration-200`, `ease-out`.
- **Layout Changes (Modals, Pages)**: `duration-300`, custom spring easing.

## 7. Icons
- Standardized on **Lucide React**.
- Stroke width: Strictly 1.5px to maintain an elegant, lightweight feel.
- Size: `w-4 h-4` for inline text, `w-5 h-5` for standard buttons, `w-8 h-8` for hero illustrations.

## 8. Accessibility
The design system architecture bakes in accessibility:
- **Focus Rings**: Replaced the default browser outline with a custom ring: `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`.
- **Contrast**: The semantic HSL variables are carefully calibrated to pass WCAG AA contrast ratios against their respective backgrounds in both light and dark modes.
