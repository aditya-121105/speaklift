# SpeakLift: Frontend Engineering Standards

This document establishes the mandatory coding standards for the SpeakLift frontend. Code that violates these standards will be rejected in Pull Requests.

## 1. Naming Conventions
- **Components & Files**: `PascalCase.tsx` (e.g., `InterviewReportCard.tsx`).
- **Hooks & Hook Files**: `camelCase` starting with `use` (e.g., `useInterviewSession.ts`).
- **Utility/Service Files**: `kebab-case.ts` (e.g., `api-client.ts`, `string-utils.ts`).
- **Types/Interfaces**: `PascalCase` (e.g., `InterviewResponseDto`). Do not prefix with `I` (e.g., `IInterviewResponseDto` is forbidden).
- **Zod Schemas**: Postfixed with `Schema` (e.g., `loginFormSchema`).

## 2. Folder Conventions
- Feature folders must adhere to the standard blueprint:
  ```text
  src/features/[feature-name]/
  ├── api/         # Service objects wrapping API calls
  ├── components/  # React components exclusive to this feature
  ├── hooks/       # Custom hooks and TanStack queries
  └── schemas/     # Zod definitions and TypeScript types
  ```

## 3. Component Responsibilities
- Keep components small. If a component exceeds 250 lines, it likely needs to be broken down into sub-components.
- Rely strictly on props for data injection. Avoid internal data fetching inside dumb UI components (`src/components/ui/`).
- Only Experience Components (Pages or top-level Feature Wrappers) should call TanStack Query hooks.

## 4. Hook Responsibilities
- Custom hooks must encapsulate all complex state logic.
- A component should not contain more than 2-3 raw `useState` or `useEffect` calls. If it does, abstract that logic into a custom hook.

## 5. Service & API Responsibilities
- The API Client (`src/lib/api-client.ts`) exclusively handles Axios configuration, intercepts, and network normalization.
- Feature API Services (e.g., `AuthService.login()`) strictly manage URL construction and payload formatting, returning strongly typed Promises. They must never interact with the DOM or React State.

## 6. Import Ordering
Organize imports using ESLint/Prettier automation to enforce this exact order:
1. React / Next.js built-ins.
2. Third-party libraries (`framer-motion`, `lucide-react`).
3. Global UI Components / Lib (`@/components/ui`, `@/lib`).
4. Feature internals (`./components/Child`, `../hooks/useData`).
5. Types and Styles.

## 7. Error Handling
- Never silence errors (`catch (e) {}` is forbidden).
- API errors must be routed to standard Toast notifications via the UI layer or caught by a structural `<ErrorBoundary>`.
- Client-side validation errors must be handled natively by `react-hook-form` and displayed inline.

## 8. Testing Expectations
- **Unit Testing**: Complex custom hooks (e.g., score calculation, timer state) must have unit tests via Jest/Vitest.
- **Component Testing**: Complex generic components must have tests via React Testing Library ensuring ARIA states function correctly.
- **E2E Testing**: Core user journeys (Login, Onboarding, Taking an Interview) will be covered by Playwright.

## 9. Performance Expectations
- Minimize Client Components (`"use client"`). Only use it at the lowest possible leaf node in the DOM tree where state or interactivity is required.
- Do not import heavy libraries (e.g., `lodash`, `moment`) if a native Web API or smaller alternative (`date-fns`) suffices.
- Avoid cascading fetches. TanStack Query should execute dependent queries explicitly via the `enabled` flag.

## 10. Accessibility Expectations
- Every `<img>` requires an `alt` attribute.
- Interactive elements must be fully keyboard navigable.
- ESLint `jsx-a11y` rules must strictly pass.

## 11. Documentation Expectations
- Complex hooks or services must include a JSDoc block explaining parameters and edge cases.
- Any workaround for third-party bugs must include an inline comment linking to the relevant GitHub issue.
