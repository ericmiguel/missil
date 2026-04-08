# Guide

This section covers everything you need to use Missil end-to-end, with annotated
examples at each step. If you're new to Missil, follow the pages in order — each
one builds on the previous.

---

## [1. JWT](jwt.md)

Start here. Missil needs a JWT token in a specific shape: a dict under a key of
your choice, where each entry maps a business area name to a numeric permission
level. This page explains that structure and shows how to issue and verify tokens.

---

## [2. Bearers](bearers.md)

A bearer is the FastAPI dependency that extracts and decodes the token on every
request. This page helps you choose between `TokenBearer` (cookie + header fallback),
`CookieTokenBearer`, and `HeaderTokenBearer`, and covers advanced topics like
token revocation and accessing the decoded claims in your route functions.

---

## [3. Access Control](access-control.md)

Once you have a bearer, you declare business areas with `AreasBase` and protect
endpoints by adding `areas.finances.READ` (or `WRITE` / `ADMIN`) as a FastAPI
dependency. This page also covers `Role` — a way to group multiple rules into a
single reusable dependency.

---

## [4. Routers](routers.md)

When many endpoints share the same base rule, `ProtectedRouter` lets you set it
once at the router level and only add stricter rules per endpoint. This page
explains how router-level and endpoint-level rules stack.

---

## [5. Exceptions](exceptions.md)

Both `TokenValidationException` and `PermissionDeniedException` are FastAPI
`HTTPException` subclasses. This page shows how to raise them manually for custom
business logic and how to override the default response format.

---

## [Migration](migration.md)

If you're upgrading from an older version that used `make_areas()` or `make_area()`,
this page has side-by-side before/after examples for migrating to `AreasBase`.
