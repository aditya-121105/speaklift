# SpeakLift: Authentication Flow

SpeakLift relies on a secure, stateless JWT authentication architecture. The frontend must manage this seamlessly, ensuring the user is never abruptly logged out during an active session unless security necessitates it.

## 1. Token Strategy
The backend issues JWT tokens.
- **Access Token**: Short-lived (e.g., 30 minutes). Used for authorizing API requests.
- **Storage**: The Access Token is stored in an `HttpOnly`, `Secure`, `SameSite=Lax` cookie via the backend. The frontend JavaScript **cannot** access this token directly, eliminating XSS token theft vectors.

## 2. Authentication Context (`useAuth`)
Since the frontend cannot read the `HttpOnly` cookie, it determines authentication state by calling a `/v1/auth/me` endpoint.

- **Initialization**: On initial app load (or via a server component layout), the app attempts to fetch the user profile.
- **Success**: The `useAuth` hook (Zustand/React Context) populates `user`, setting `isAuthenticated = true`.
- **Failure (401)**: The app recognizes the user is unauthenticated.

## 3. Protected Routes Enforcement
- **Middleware Level**: Next.js `middleware.ts` intercepts requests to `/dashboard`, `/interviews`, etc. It checks for the *existence* of the auth cookie. If missing, it immediately redirects to `/login`.
- **Client Level**: If the token expires during a session and an API call returns `401 Unauthorized`, the Axios interceptor catches it, clears the `useAuth` state, and redirects the user to `/login?session_expired=true`.

## 4. Automatic Refresh
Currently, SpeakLift relies on a standard Access Token. When Refresh Tokens are implemented:
- The Axios interceptor will intercept the `401` error.
- It will pause all pending outgoing requests.
- It will hit the `/v1/auth/refresh` endpoint (which relies on an `HttpOnly` refresh cookie).
- If successful, it resumes all paused requests transparently. The user never notices.
- If the refresh fails, the user is logged out.

## 5. Logout
- The user clicks "Logout".
- The frontend calls `POST /v1/auth/logout`.
- The backend clears the `HttpOnly` cookies.
- The frontend clears the `useAuth` state and the TanStack Query cache (`queryClient.clear()`) to prevent sensitive data from lingering in memory.
- The user is redirected to `/login`.

## 6. Future OAuth Compatibility
The architecture is designed to support OAuth (Google, GitHub) via NextAuth.js or custom backend handlers. The UI flow will remain identical—the user clicks "Login with GitHub", the backend issues the `HttpOnly` cookie, and `/v1/auth/me` populates the context.
