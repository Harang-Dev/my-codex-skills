# AlphaSquare Review Risks

Read this reference only when reviewing the AlphaSquare monorepo. Apply the relevant sections after reading the repository's current `AGENTS.md` and package-level instructions; those files remain authoritative.

## Shared ownership and blast radius

- Treat `packages/modules` as the shared source of truth. Search desktop, mobile, alphachart, and alphachart-guest consumers whenever an export, type, component contract, constant, config, or runtime assumption changes.
- Keep app-specific UI and policy in the owning app package unless reuse or correctness requires a shared implementation.
- Prefer `@as/modules`, design-system components, shared layout primitives, and existing wrappers over local duplicates.
- Treat new exports, global registrations, base-class overrides, and shared utilities as public API. Require a real consumer or framework role.

## Service-layer ownership

- Keep raw fetching and TanStack Query mechanics in `composables/service/cache`; do not move view orchestration, UI validation, or save-flow policy there.
- Keep singleton cross-app synchronization in `global`, independently instantiated state in `local`, and feature coordination across layers in `orchestration`.
- Verify query keys contain every result-changing input. For mutations, inspect invalidation, optimistic state, rollback, stale responses, and duplicate-submit protection.

## Domain state and lifecycle

- On stock, user, account, route, or feature-key changes, prevent old requests or cached values from appearing under the new identity.
- Apply the same feature-flag and availability guard to initial, ready, reconnect, watcher, and cached paths.

## Financial and market correctness

- For prices, orders, payments, rankings, charts, and market data, verify units, sign, ordering, precision, rounding, nullability, and identity across display, comparison, cache, and API payload paths.
- Check slow responses and rapid stock/account switches for stale data, wrong-account actions, double submission, or out-of-order commits.
- Avoid introducing floating-point assumptions for money-like values unless the existing domain contract explicitly uses them.

## Persisted and generated contracts

- Search local/session storage, saved settings, fixtures, mocks, server producers, cache keys, and spread/copy paths when shared fields or shapes change.
- Require a clear normalization, migration, version, or reset strategy for old persisted values; flag unexplained dual contracts.
- Treat Socket.IO price bindings as generated from the pinned `vendor/alpha-contracts` submodule. Verify intentional submodule upgrades and regeneration through `scripts/generate-price-protobuf.sh`; do not accept manual generated-code edits as the source change.
