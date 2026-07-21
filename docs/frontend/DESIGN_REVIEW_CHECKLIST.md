# SpeakLift: Design Review Checklist

Before any PR merging frontend changes can be approved, the author and reviewer must ensure the implementation satisfies the following criteria.

## 1. Product & UX
- [ ] **Goal Orientation**: Does the screen immediately answer *why* the user is here and *what* they should do next?
- [ ] **Progressive Disclosure**: Are advanced settings or analytics hidden behind a secondary click to avoid overwhelming the user?
- [ ] **Empty States**: Does the screen handle the lack of data gracefully? Does it offer an action to populate the data?
- [ ] **Error States**: Are API failures handled with empathetic copy and a clear recovery path (e.g., "Retry") rather than raw technical error strings?

## 2. Design & Consistency
- [ ] **Spacing Rhythms**: Are all margins and padding strictly adhering to the 4pt grid system?
- [ ] **Typography Hierarchy**: Are headings, body text, and captions using the correct scale and weights as defined in the Design System?
- [ ] **Token Usage**: Does the PR exclusively use semantic design tokens (`--surface-elevated`, `--text-muted`) instead of raw colors (`gray-800`, `white`)?
- [ ] **Dark Mode Integrity**: Have all new visual elements been manually tested in both Light and Dark mode?

## 3. The AI Experience
- [ ] **Visual Anchor**: Does the AI utilize "The Spark" and `--ai-accent` color properly?
- [ ] **Latency Mitigation**: Are streaming text effects, typing indicators, or morphing mesh gradients used to obscure backend response latency?
- [ ] **Proactive Stance**: If applicable, does the AI feature present actionable items (Action Cards) rather than just passive text walls?

## 4. Accessibility (a11y)
- [ ] **Keyboard Navigable**: Can a user tab through all interactive elements in a logical sequence?
- [ ] **Focus Rings**: Are custom `focus-visible` rings present and clear?
- [ ] **Touch Targets**: Are all clickable elements on mobile at least 44x44 CSS pixels?
- [ ] **Contrast & Screen Readers**: Do colors pass WCAG AA standards? Are decorative elements hidden from screen readers via `aria-hidden="true"`?

## 5. Performance
- [ ] **Client Components**: Are `"use client"` directives pushed down the tree as far as possible to maximize Server Components?
- [ ] **Bundle Size**: Were any heavy third-party libraries introduced? Was an ADR approved for their inclusion?
- [ ] **Loading States**: Are skeleton screens utilized instead of spinners for full-page or full-card data fetching?

## 6. Architecture & Engineering
- [ ] **Feature Isolation**: Does the PR adhere to the `src/features/*` folder structure? Did any domain logic leak into the generic `src/components/ui/` folder?
- [ ] **State Separation**: Are Server State (TanStack) and Client State (Zustand/useState) strictly separated?
- [ ] **API Abstraction**: Are all network calls routed through a feature Service and the central `api-client`, avoiding raw `fetch()` calls in components?
