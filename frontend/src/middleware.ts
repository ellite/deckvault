import { defineMiddleware } from "astro:middleware";

const PUBLIC_ROUTES = ["/login", "/register", "/offline", "/sw.js", "/manifest.webmanifest"];

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
    return next();
  }

  const token = context.cookies.get("deckVault_token");
  if (!token?.value) {
    return context.redirect("/login");
  }

  return next();
});
