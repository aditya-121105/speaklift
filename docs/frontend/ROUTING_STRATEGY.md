# SpeakLift: Routing Strategy

SpeakLift leverages Next.js App Router for its routing infrastructure. The routing strategy emphasizes logical grouping, route protection, and seamless transitioning via nested layouts.

## Route Architecture

### 1. Public Routes
- **`/`**: Marketing landing page.
- **`/pricing`**, **`/about`**: Standard marketing pages.
- Public routes do not check for authentication state aggressively, though they may detect an active session to swap a "Login" button for a "Dashboard" button.

### 2. Route Groups
We use Next.js Route Groups (folders wrapped in parenthesis) to apply shared layouts without affecting the URL structure.

#### `(auth)`
- **`/login`**, **`/register`**, **`/forgot-password`**
- Uses a minimalist layout devoid of standard navigation, focusing user attention entirely on the authentication form.

#### `(dashboard)`
- **`/dashboard`**, **`/interviews`**, **`/profile`**
- Applies the core application layout (Sidebar, Header, Command Palette).
- Guarded heavily by authentication middleware.

### 3. Protected Routes
Route protection is enforced at two levels:
1. **Next.js Middleware (`middleware.ts`)**: Checks for the existence of an HTTP-only JWT cookie. If absent, it immediately redirects the user to `/login` before rendering any React components, preventing the flash of unauthenticated content.
2. **Client-side Guards**: The `useAuth` hook verifies the integrity of the user state and handles token expiration events gracefully during an active session.

### 4. Nested Layouts
The app uses nested layouts to preserve state and avoid unnecessary re-renders across route changes.
- `app/layout.tsx`: Root HTML/Body injection, Theme Provider, and TanStack Query Provider.
- `app/(dashboard)/layout.tsx`: Persistent sidebar navigation and global AI context provider.

### 5. Loading and Error Boundaries
Every significant route or nested layout must define:
- **`loading.tsx`**: Renders a skeleton UI matching the exact dimensions of the target page to ensure layout stability while data is fetched.
- **`error.tsx`**: Catches rendering and data-fetching errors gracefully. Must offer a highly styled, empathetic "Try Again" button to recover without a hard refresh.
- **`not-found.tsx`**: A customized 404 page that maintains the brand identity and offers quick links back to the dashboard.

### 6. Future Admin Routes
- **`/admin/*`**
- Will utilize its own Route Group `(admin)` with strict Role-Based Access Control (RBAC) enforced explicitly in Next.js middleware checking for `role: "admin"` in the decoded JWT.
