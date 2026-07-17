import { defineMiddleware } from "astro:middleware";

const PUBLIC_ROUTES = ["/login", "/register", "/offline", "/sw.js", "/manifest.webmanifest"];

const SECURITY_HEADERS: Record<string, string> = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy":
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline'; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: https://images.igdb.com; " +
    "connect-src 'self'; " +
    "font-src 'self'; " +
    "frame-ancestors 'none';",
};

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  if (
    PUBLIC_ROUTES.some((r) => pathname.startsWith(r)) ||
    pathname.startsWith("/_astro") ||
    pathname.startsWith("/icons") ||
    pathname.startsWith("/logo") ||
    pathname.startsWith("/api/auth/login") ||
    pathname.startsWith("/api/auth/register") ||
    pathname.startsWith("/api/auth/logout")
  ) {
    const response = await next();
    for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
      response.headers.set(key, value);
    }
    return response;
  }

  const token = context.cookies.get("deckVault_token");
  if (!token?.value) {
    return context.redirect("/login");
  }

  const response = await next();
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    response.headers.set(key, value);
  }
  return response;
});
