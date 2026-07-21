# SpeakLift: State Management

SpeakLift enforces a strict separation of concerns regarding state. Mixing Server State with UI State in a single global store (like traditional Redux) is an anti-pattern. 

## 1. Server State (TanStack Query)
**Owner**: `@tanstack/react-query`

Server state is data that lives on the backend and is fetched by the frontend. It is asynchronous, mutable by multiple clients, and potentially stale.

- **Usage**: Used for almost all data in SpeakLift (User Profile, Interview Reports, Question Banks).
- **Behavior**: Handles caching, background refetching, pagination, and optimistic updates.
- **Rule**: Never copy Server State into Client State. Do not fetch data with TanStack Query and then run `setGlobalUser(data)`. Components should consume data directly from the `useQuery` hook.

## 2. Client/Global State (Zustand)
**Owner**: `zustand`

Client state is synchronous, ephemeral data that affects the entire application but does not persist to the database.

- **Usage**: Command Palette visibility toggle, current active theme, global alert banners, or complex multi-step wizard progression that hasn't been submitted yet.
- **Behavior**: Fast, reactive, and minimal boilerplate.
- **Rule**: Keep the Zustand store as small as possible. If state can be localized to a single component or Context, it should not be in Zustand.

## 3. UI/Local State (React `useState` / `useReducer`)
**Owner**: React (`useState`, `useRef`)

State that is only relevant to a specific component or its immediate children.

- **Usage**: Dropdown open/closed states, current active tab, hover states, local input buffers before form submission.
- **Rule**: Prefer local state whenever possible. Elevate to Context or Zustand only when prop-drilling becomes unmanageable.

## 4. Form State (React Hook Form)
**Owner**: `react-hook-form`

Managing input validation, touched states, and dirty states.

- **Usage**: Login forms, profile editing, interview settings configuration.
- **Behavior**: Uncontrolled inputs optimized for performance. Validated strictly by Zod schemas that mirror backend DTOs.
- **Rule**: Never use `useState` for complex forms. Always rely on RHF.

## 5. Theme State (next-themes)
**Owner**: `next-themes`

- **Usage**: Managing Light/Dark/System preference.
- **Behavior**: Integrates directly with Tailwind CSS classes (`dark:bg-slate-900`) and prevents the dreaded "white flash" on load by injecting a tiny script into the `head`.

## 6. Streaming AI State (Future-Proofing)
**Owner**: Custom Hooks leveraging Web Streams API.

When SpeakLift implements streaming AI responses (e.g., text generation character-by-character):
- **Usage**: The streaming chunk buffer will be managed via a dedicated custom hook (`useAiStream`) utilizing `useReducer` or raw `useState`. 
- **Rule**: Streaming state must be isolated from the global store to prevent application-wide re-renders during high-frequency stream updates. Once a stream completes, the final aggregated string may be passed to TanStack Query's cache.
