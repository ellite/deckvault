import type { APIRoute } from "astro";
import { apiFetch } from "../../lib/api";

// Catch-all proxy: forwards every /api/* request to the FastAPI backend
// stripping the /api prefix so /api/auth/login → /auth/login on the backend.
export const ALL: APIRoute = async ({ request, params }) => {
  const path = params.path ?? "";
  const url = new URL(request.url);
  const backendPath = `/${path}${url.search}`;
  const cookieHeader = request.headers.get("cookie") ?? "";

  const body = ["GET", "HEAD"].includes(request.method)
    ? undefined
    : await request.text();

  let upstreamRes: Response;
  try {
    upstreamRes = await apiFetch(backendPath, {
      method: request.method,
      cookies: cookieHeader,
      body: body || undefined,
      headers: {
        "Content-Type": request.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ detail: "Could not reach backend" }), {
      status: 502,
      headers: { "content-type": "application/json" },
    });
  }

  const headers = new Headers();
  const contentType = upstreamRes.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const setCookie = upstreamRes.headers.get("set-cookie");
  if (setCookie) headers.set("set-cookie", setCookie);

  const responseBody = upstreamRes.status === 204 ? null : await upstreamRes.text();

  return new Response(responseBody, { status: upstreamRes.status, headers });
};
