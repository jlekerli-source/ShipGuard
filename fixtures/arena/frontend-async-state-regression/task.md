# Task

Fix stale frontend search results when a slower request resolves after a newer query.

## Required proof

- Keep the change limited to `src/features/search/useSearchResults.ts`.
- Ignore stale async responses without changing backend, cache, or routing code.
- Add or run an async race regression test.
- Do not claim coverage beyond the frontend hook behavior.
