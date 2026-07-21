# SpeakLift: Project Structure

We follow a **Feature-First Architecture**. Instead of grouping files by technical type (e.g., placing all hooks in one folder, all components in another), we group by domain feature. This ensures that as the codebase grows, features remain isolated, cohesive, and easy to safely delete or refactor.

## Directory Hierarchy

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router (Routing, Layouts, Pages)
│   │   ├── (auth)/             # Route group: Authentication flows
│   │   ├── (dashboard)/        # Route group: Authenticated dashboard
│   │   ├── admin/              # Future admin panel
│   │   └── api/                # Next.js API Routes (BFF proxy if needed)
│   │
│   ├── features/               # Domain-specific modules (The Core of the App)
│   │   ├── interviews/         # Interview session domain
│   │   │   ├── api/            # API services specific to interviews
│   │   │   ├── components/     # UI components strictly for interviews
│   │   │   ├── hooks/          # React hooks (TanStack Query) for interviews
│   │   │   └── schemas/        # Zod validation schemas
│   │   ├── reports/            # Interview intelligence reporting domain
│   │   ├── profile/            # Candidate profile & resumes
│   │   └── onboarding/         # Initial user setup
│   │
│   ├── components/             # Global, domain-agnostic generic components
│   │   ├── ui/                 # shadcn/ui components (Buttons, Inputs)
│   │   ├── layout/             # Global layout components (Navbar, Sidebar)
│   │   └── ai/                 # Generic AI widget framework
│   │
│   ├── lib/                    # Core configuration and generic utilities
│   │   ├── api-client.ts       # Axios instance & interceptors
│   │   ├── store.ts            # Global Zustand store definition
│   │   ├── cn.ts               # Tailwind class merging utility
│   │   └── utils/              # Generic string/date formatting
│   │
│   ├── hooks/                  # Global hooks not tied to a specific feature
│   │   ├── use-auth.ts         # Authentication context hook
│   │   └── use-media-query.ts  # Responsive design hook
│   │
│   ├── types/                  # Global TypeScript type definitions
│   │   └── index.d.ts
│   │
│   ├── styles/                 # Global CSS (globals.css, Tailwind config)
│   └── assets/                 # Static assets (fonts, images, icons)
```

## Folder Responsibilities

### `src/app/`
Contains strictly routing logic. Files here (`page.tsx`, `layout.tsx`, `loading.tsx`) should be as thin as possible, primarily importing components from the `features/` directory.

### `src/features/`
The backbone of the application. If a component, hook, or schema is only used within the context of an "Interview", it lives in `features/interviews/`. This prevents the global `components/` folder from becoming a cluttered dumping ground.

### `src/components/ui/`
Reserved exclusively for dumb, stateless, highly reusable primitive components generated via `shadcn/ui`. These components possess no business logic.

### `src/lib/`
Contains code that initializes external libraries or performs generic transformations. `api-client.ts` sets up the Axios instance, but does not define specific API endpoints.
