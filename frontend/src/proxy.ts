import { NextResponse } from "next/server";

// Define protected and guest-only routes
export function proxy() {
  // Note: For SpeakLift v1, we use localStorage for the token (zustand persist).
  // This means the middleware cannot directly read the token securely without HTTP cookies.
  // Ideally, backend sets an HttpOnly cookie, but if using standard JWTs in localStorage,
  // middleware protection is limited. We'll check for a general cookie if one is set,
  // otherwise client-side route guards will be the primary protection mechanism.
  // For now, we will assume a "speaklift-auth" cookie exists IF we transition to cookies,
  // or we just let the client side handle it if no cookie is present.
  // However, Next.js middleware is best used when cookies are present.

  // As per architecture: "Authentication status is determined through backend session validation"
  // For a robust system without HttpOnly cookies right now, client-side route guards are more effective
  // because Zustand accesses localStorage. 
  
  // If we want basic server-side gating (assuming a future cookie `auth_token`), it goes here.
  // const token = request.cookies.get("auth_token");

  // Allow next-auth or similar cookie logic. For now, pass through and let client-side protect.
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
