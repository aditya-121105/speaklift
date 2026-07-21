# SpeakLift: Frontend Architecture Freeze v1.0

## Official Freeze Declaration
As of Sprint C3.5, the SpeakLift v1.0 Frontend Architecture is **officially frozen**. The product vision, UX philosophy, architecture boundaries, and design system documented in `docs/frontend/` are the authoritative source of truth. All future engineering implementation must conform to this specification unless a formal Frontend Architecture Decision Record (ADR) is proposed and approved.

---

## 1. Product Identity
SpeakLift is an **AI Career Coach**, not a traditional LMS or static dashboard. The experience must be minimal, premium, intelligent, dynamic, and inherently human, prioritizing speed and personalization for Gen Z and young millennials preparing for high-stakes interviews.

## 2. Technology Stack
The official frozen stack is:
- **Core**: Next.js (App Router), React, TypeScript
- **Styling**: Tailwind CSS, shadcn/ui
- **State Management**: TanStack Query (Server State), Zustand (Client State)
- **Forms**: React Hook Form, Zod
- **Motion & Visualization**: Framer Motion, Recharts
- **Networking**: Axios

## 3. Layered Architecture
Strict downward dependencies are enforced:
**Pages → Feature Modules → Hooks → Services → API Client → Backend**
Cross-feature coupling is forbidden. Shared logic must reside in `src/components/`, `src/hooks/`, or `src/lib/`.

## 4. Folder Structure
The architecture relies on a **Feature-First** structure (`src/features/*`), where components, hooks, schemas, and API wrappers specific to a domain (e.g., `interviews`, `reports`) are co-located.

## 5. Routing Strategy
Leveraging Next.js App Router:
- **Route Groups**: Used to cleanly segregate `(auth)` vs `(dashboard)` layouts.
- **Protection**: Enforced sequentially via Next.js Middleware (cookie presence) and client-side context (session validation).
- **Error Boundaries**: Every major nested layout must implement `loading.tsx` and `error.tsx` for graceful degradation.

## 6. State Management
- **TanStack Query** owns all asynchronous, backend-derived Server State.
- **Zustand** owns all synchronous, ephemeral Client State.
- **React Hook Form** owns all validation and form buffer state.
- Mixing server data into global client stores is strictly an anti-pattern.

## 7. Authentication Strategy
Secure, stateless JWT architecture using `HttpOnly` cookies. The frontend evaluates state via `/v1/auth/me`. Expired sessions pause outgoing requests, prompt re-authentication (or background refresh), and retry smoothly to prevent data loss.

## 8. API Layer
All networking routes through a centralized Axios client in `src/lib/api-client.ts`. It enforces global timeouts, injects `X-Client-Trace-Id` headers, automatically standardizes errors for TanStack Query, and provides an escape hatch for future Web Streams.

## 9. Design System
- **Tokens**: Semantic tokens (e.g., `--surface-elevated`) defined via HSL in `globals.css`.
- **Spacing**: Strict 4pt grid system (`gap-4`, `p-6`).
- **Typography**: Geometric sans-serif (`Inter`/`Geist`), tight tracking on display fonts, and `tabular-nums` for numeric components.
- **Dark Mode**: Dark-mode-first mentality utilizing deep slates, avoiding `#000000` to minimize eye strain.

## 10. Motion Philosophy
Animations obscure latency and build physical realism via spring physics. Standard layout transitions take `300ms`; AI streaming text generates character-by-character to create the illusion of thought. Support for OS-level `prefers-reduced-motion` is mandatory.

## 11. Accessibility Philosophy
WCAG AA compliance is a first-class requirement. 
- Minimum 44x44 CSS pixel touch targets.
- Strict reliance on explicit focus rings (`focus-visible:ring-primary`).
- Keyboard navigability across all interactive elements via native semantic HTML or Radix ARIA attributes.

## 12. AI Identity
The AI operates under a cohesive visual language ("The Spark"). It utilizes morphing mesh gradients for "Thinking" states and streams text dynamically. It acts proactively through personalized insights and action-oriented roadmap tasks.

## 13. Future Compatibility
The architecture is explicitly designed to absorb:
- **Voice Interviews**: via generic hardware hooks isolated from UI logic.
- **Real-Time Streaming**: via dedicated Service-layer fetch wrappers bypassing Axios.
- **Mobile Ecosystems**: via strict separation of business logic (Hooks/Services) from view logic (Components).
