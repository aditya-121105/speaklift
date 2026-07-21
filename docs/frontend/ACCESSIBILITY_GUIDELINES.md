# SpeakLift: Accessibility Guidelines

Accessibility is not an afterthought or a compliance checklist. A premium product is inherently accessible to everyone. The SpeakLift frontend must be engineered so that a visually impaired user navigating via screen reader experiences the same high-quality AI coaching as a sighted user.

## 1. Color Contrast
- **Requirement**: WCAG 2.1 AA compliance across the entire application.
- **Execution**: The semantic color tokens defined in `globals.css` are mathematically verified for contrast against their backgrounds. Text must have a minimum contrast ratio of 4.5:1 against its background. Large text (18pt+) requires 3:1.
- **Dark Mode**: Dark mode is often where contrast fails. Ensure that `--text-muted` does not become invisible against `--background`.

## 2. Keyboard Navigation
- **Requirement**: The entire application must be perfectly navigable using only the `Tab`, `Shift+Tab`, `Enter`, `Space`, and `Arrow` keys.
- **Execution**:
  - Semantic HTML elements (`<button>`, `<a>`, `<input>`) must be used appropriately to inherit native browser keyboard behaviors.
  - Custom interactive elements (e.g., custom dropdowns) must implement `tabindex="0"` and listen for `keydown` events.

## 3. Focus Visibility
- **Requirement**: The user must always know exactly which element has keyboard focus.
- **Execution**: We do not rely on the browser's default blue halo, as it often clashes with the brand.
- Every interactive component includes: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`. 
- **Rule**: Never use `focus:outline-none` without providing a custom `focus-visible` alternative.

## 4. Screen Reader Compatibility (ARIA)
- **Execution**:
  - All icons must have `aria-hidden="true"` if they are purely decorative.
  - Icon-only buttons must have an `aria-label` or visually hidden text (`<span class="sr-only">`).
  - Complex widgets (Tabs, Dialogs, Accordions) rely on Radix Primitives (via shadcn/ui), which handle complex ARIA state bindings (e.g., `aria-expanded`, `aria-controls`) automatically.

## 5. Reduced Motion
- **Requirement**: Users prone to vestibular motion sickness must be accommodated.
- **Execution**: Use Tailwind's `motion-reduce:` variants.
- Example: `transition-transform motion-reduce:transition-none hover:scale-105`.
- Framer Motion animations must check the `useReducedMotion()` hook and instantly snap to the final state if true.

## 6. Touch Targets
- **Requirement**: Prevent accidental taps on mobile devices.
- **Execution**: All interactive elements (buttons, links, checkboxes) must have a minimum interactive area of **44x44 CSS pixels**. Even if a button visually looks smaller (e.g., a tiny `w-4 h-4` close icon), it must have sufficient padding or a larger invisible wrapper to meet the 44px threshold.

## 7. Responsive Flow & Zoom
- **Requirement**: The UI must not break when the user zooms the page to 200%.
- **Execution**: Avoid hardcoded pixel heights (`h-10`) on text containers. Allow text to wrap and containers to expand vertically. Use `min-h-[Xpx]` instead of absolute heights when possible.
