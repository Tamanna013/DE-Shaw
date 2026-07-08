# TestLens Frontend

The primary UI surface for TestLens, built with React, Vite, TailwindCSS, and TanStack Query.

## Architectural Choices

### Server State Management (TanStack Query)
We rely exclusively on **TanStack Query** for all remote data fetching and caching. We specifically avoid `useEffect` + `fetch` chains. This provides out-of-the-box loading states, error boundaries, caching, and background refetching (essential for the Dashboard where CI metrics update constantly).

### Client State Management
We use local component state (via `useState`) for localized UI logic (like toggling a dropdown or filling a form). For cross-cutting UI state like the Dark Mode theme toggle, we rely on a minimal React hook (`useTheme.ts`) rather than pulling in a heavy global state library like Redux. 

*Why no Redux?* TestLens is a data-heavy application where 95% of state is "Server State" (managed by TanStack Query). The remaining 5% of "Client State" is too trivial to warrant the boilerplate, bundle size, and architectural complexity of Redux. If complex cross-component client state arises in the future, we will adopt `Zustand`.

### Dark Mode Toggle
The `useTheme.ts` hook manages the theme toggling. Note that in this artifact environment, it relies entirely on React State rather than `localStorage`. Real-world deployments would persist this preference via `localStorage` or a cookie, but this artifact avoids `localStorage` to prevent throwing `DOMException` cross-origin errors if loaded in a sandboxed iframe.

### API Client Resilience
The `api/client.ts` wrapper enforces a strict contract:
1. It injects the `Authorization: Bearer <token>` header into every request.
2. If it detects a `401 Unauthorized`, it intercepts the response, attempts a silent token refresh, and retries the original request exactly once.
3. If the retry also fails with a 401, it hard-redirects the user to the `/login` route, guaranteeing that users are never stuck on a broken page with an expired session.
