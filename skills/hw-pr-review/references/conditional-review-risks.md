# Conditional Review Risks

Read only the sections selected by the routing table in `SKILL.md`. Apply repository instructions before these general prompts.

## Generated and External Artifacts

- Confirm generated status from `.gitattributes`, file headers, repository instructions, or codegen configuration rather than the filename alone.
- Compare schema/source/generator changes with output changes. Flag missing output or output-only manual edits, and propose fixing the source of truth rather than generated code.
- Review lockfiles against manifests for intended direct changes, registry/source/version drift, and unrelated churn.
- For submodules, inspect the old/new commit range and follow-up generation obligations. For binary, LFS, minified, or vendored output, verify provenance and report what cannot be inspected.
- Run mutating regeneration only in fix mode or an isolated disposable worktree, using the pinned generator/version.

## Persisted Data and Migration

- Search storage, cookies, caches, server producers, fixtures, mocks, saved settings, and import/export paths for old values.
- Verify producer/consumer compatibility, defaults, nullability, versioning, migration idempotence/rollback, explicit reset, or safe rejection.
- Treat mixed old/new contracts as intentional only with a clear owner, duration, and removal plan.

## Shared and Cross-Package Surface

- Search every export, constructor, call site, object spread, mock, fixture, and documentation example.
- Verify that app-local behavior was not unnecessarily promoted to a shared or global layer.
- Check compatibility and rollout for consumers that cannot update atomically.

## Security and Privacy

- Trace untrusted sources to HTML, URL, query/header, command, file, log, analytics, storage, and network sinks.
- Verify server-side authorization boundaries, validation/escaping location, CSRF and redirect behavior, and secret or personal-data handling.
- Redact any discovered secret from output. Report a finding only for a reachable data flow or explicit policy violation; turn an unclear sanitizer or permission boundary into a verification question.
- Treat security as a category. Derive priority from demonstrated reachability, impact, and likelihood.

## Financial and Other High-Impact Data

- Verify units, sign, identity, ordering, precision, rounding, nullability, idempotency, and display-versus-domain values.
- Trace slow, duplicated, retried, or out-of-order operations through payload, cache, and commit paths.
- Require stronger regression protection for money, order, permission, quota, destructive, or irreversible operations.

## Feature Flags and Rollout

- Verify default, loading/not-ready, OFF, unsupported, reconnect, watcher, and cached-state behavior.
- Confirm that flag and capability checks guard every side-effect entry path, not only initial render.
- Check cleanup or migration when rollout state changes during a session.

## UI, Layout, and Accessibility

- Prefer native semantics and established controls; verify accessible name, keyboard parity, focus trap/restore, and real disabled/readonly behavior.
- Trace loading, error, empty, unavailable, long-content, first-render, responsive, dynamic announcement, and reduced-motion paths when relevant.
- Do not demand unnecessary ARIA from a native element or infer contrast/screen-reader/visual correctness from code alone. Record exact manual QA when runtime verification is needed.
- Run DOM measurement only after a stable render point supported by the framework.

## Performance and Resources

- Estimate realistic collection size and call frequency for render/watch loops, sorting/filtering, polling, retries, startup, and per-row work.
- Check request counts, algorithmic growth, bundle impact, duplicate subscriptions, and cleanup of timers/listeners/observers.
- Require a reachable unbounded path, measurement, profile, or concrete count before promoting micro-optimization preferences to findings.

## Dependency and Framework Integration

- Search for an existing project wrapper or shared primitive before adding local integration code.
- Verify the installed version's defaults, values/events, lifecycle, cleanup, cancellation, retries, bundle/provenance impact, and migration behavior using local source or primary documentation.
- Remove obsolete imports, types, helpers, comments, and configuration from the previous integration.

## Mechanical Migration and Policy

- Define the old and new contracts, then search exhaustively for stale patterns, mixed usage, incomplete consumers, invalid examples, and ambiguous exceptions.
- Check rename/delete, case-only rename, file modes, symlinks, path aliases, persisted keys, documentation, fixtures, and enforcement tests.
- Do not rely on representative spot checks for broad migrations.
