---
name: hw-pr-review
description: Run a PR-readiness self-review on local or branch changes for human review or final readiness. Use when Codex has implemented or refactored code and needs to catch avoidable reviewer feedback, especially issues around repository conventions, ownership boundaries, component API contracts, state/lifecycle edge cases, UI/layout code paths, naming, minimality, PR-body drift, and validation claims.
---

# HW PR Review

## Purpose

Use this skill as a PR-readiness review pass. The goal is to catch issues that are not necessarily test failures: over-defensive code, thin wrappers, ambiguous names, stale comments, duplicated fallback paths, unclear ownership, and mismatches between implementation and PR explanation.

This skill applies to new work and to changed work. Do not reserve it only for refactors or review-comment followups.

## Operating Rules

- Treat the current diff as if a skeptical reviewer will read it line by line.
- If the work is attached to an existing pull request or remote review, treat existing PR body, unresolved review threads, general comments, and CI/check state as first-class review inputs. Do not start from the local diff alone when reviewer context is available.
- Prefer minimal correct code over defensive code that duplicates responsibilities.
- Separate behavior preservation from implementation convenience.
- For every materially changed element with callers or consumers, review its public surface and call sites before reading its implementation. Preserve the consumer-first model long enough to compare it with the actual behavior; do not rationalize an awkward contract with implementation knowledge.
- Do not commit while using this skill unless the user explicitly asks.
- Passing validation never proves minimality, ownership, or scope correctness.
- If changes are needed, edit locally, run the relevant checks, and show the diff before commit or push.
- If you edit during review, still report the original finding that caused the edit; do not hide it by saying there were no findings.
- If no changes are needed, say that explicitly and list residual risks.

## Workflow

### 1. Establish The Review Surface

Inspect the local diff and changed files:

```bash
git status --short
git diff --stat
git diff
```

If the work is already committed on the branch, also inspect the branch diff against the default branch:

```bash
base="$(git symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null || echo origin/main)"
git diff --stat "$base"...HEAD
git diff "$base"...HEAD
```

If there are unrelated dirty files, identify them and ignore them unless they directly affect the current work.

### 2. Reconstruct The Contract

Write down the work contract in concrete terms before reviewing code:

- What user-visible behavior must be preserved?
- What behavior was added or changed?
- What code areas are intentionally out of scope?
- What regressions would be unacceptable?
- What validation has actually run, and what remains unverified?

Use the user's latest requirements, task/goals docs, PR body, and review comments when available.

If reviewing an existing PR or remote branch that likely has a PR:

- Resolve the PR number or URL from the branch, local git metadata, or GitHub tooling.
- Read the PR title/body, unresolved review threads, non-resolved inline comments, general comments, latest review states, and failing/pending checks before finalizing the review contract.
- Separate already-known reviewer feedback from new findings. Do not repeat existing comments as if newly discovered unless the user asked for a consolidated review; instead, say whether each known issue is still valid.
- If PR context cannot be fetched, state that limitation and continue from the local diff with that residual risk.

Classify the changed responsibilities before deep review. A single PR may have multiple categories:

- Runtime behavior: user flows, UI state, service/cache behavior, async side effects, validation, permissions, feature flags.
- API or type contract: exported types, props/emits/slots, composable return shapes, event names, route/query formats, request/response payloads.
- Persisted or external data contract: localStorage/sessionStorage, IndexedDB, cookies, cache keys, server data, fixtures, mocks, saved settings, serialized objects, import/export formats.
- Shared surface: modules, shared components, constants/config, global registration, base classes, generated types, design-system primitives.
- Mechanical migration: broad renames, codemods, key/path migrations, file moves, dependency swaps, formatting-only changes.
- Policy or documentation: architecture rules, coding conventions, migration guides, public examples, test strategy, operational runbooks.

For each category in scope, write the specific contract it changes and the compatibility expectation. If the category is intentionally out of scope, record why.

### 3. Outside-In Consumer Contract Pass

For every added or materially changed element that has callers or consumers (including exported functions, composables, components, props, emits, slots, types, event payloads, config objects, routes, and shared constants), review outside-in before reading its implementation:

1. Inspect only its consumer-visible name, signature, exported types, documentation, and directly affected call sites. Do not open the implementation body yet.
2. Record the contract a reasonable caller would infer: purpose, inputs and outputs, ownership, side effects, error/nullability behavior, lifecycle or cleanup expectations, and any compatibility assumptions.
3. Record where a caller must rely on hidden knowledge or where use feels awkward: surprising argument order or defaults, required call sequencing, implicit state, unclear return or error semantics, non-obvious cleanup, duplicated ceremony, or names that conceal the real responsibility.
4. Only then read the implementation. Compare its actual contract with the consumer-first model and report mismatches, hidden obligations, and avoidable call-site friction. Do not dismiss a mismatch merely because the current implementation makes it work.

Apply this pass to direct consumers first. Expand through the repository when the changed surface is shared, exported, persisted, or cross-package. You do not need to print the full record unless it produces a finding, but do not conclude that an API is reviewer-ready without performing this comparison.

### 4. Set Review Depth

Keep the review focused on the changed surface.

- Start with changed files and directly affected call sites.
- Expand to package-wide or repo-wide search only when the diff changes shared modules, exported types, component contracts, service/cache behavior, routing, global state, feature flags, or runtime lifecycle.
- Treat docs-only changes, copy changes, and localized styling changes with a lighter pass unless they change documented contracts, reusable guidance, or shared UI behavior.
- For large mechanical migrations, do not rely on spot-checking representative files. Define the old contract and new contract, then search for remaining old patterns, mixed contracts, un-migrated consumers, persisted-data compatibility gaps, and representative runtime entry points.
- For policy, naming, documentation, or convention changes, review whether examples, names, ownership boundaries, and allowed exceptions consistently match the policy. The main risk is often ambiguous guidance rather than failing code.
- Prefer a few concrete findings over a long list of speculative possibilities.

### 5. Minimality Pass

Look for code that exists because of fear rather than a proven responsibility:

- Thin wrappers: any class, subclass, adapter, composable, helper, module registration, or event wrapper whose only behavior is forwarding to another API, setting one attribute/style, renaming an operation, or calling a single helper.
- Guard helpers whose name adds less clarity than the inline condition.
- Fallback listeners that duplicate library behavior.
- State variables that are not used by rendering, computed values, or watchers.
- Platform checks that can be replaced by event capability checks.
- Comments that explain code that should be self-explanatory.

Before deciding there are no findings, build a changed-responsibility ledger for every added or materially changed class, exported function, helper, listener, observer, module registration, state variable, and CSS selector:

- Name / location
- Call sites
- Responsibility
- Could this be local, inline, or deleted?
- Does it expand scope beyond the user's request?
- Decision: Keep / Inline / Remove / Rename
- Reason

Do not report "No findings" until this ledger has been evaluated. You do not need to print the full ledger unless it affects the answer, but you must use it.

For each item, decide:

- Keep: it owns a distinct responsibility, reduces repeated call-site complexity, isolates a real external contract, or is required by a framework extension point.
- Inline: it is a thin wrapper with no additional semantic value.
- Remove: it duplicates another code path or no longer has a caller.
- Rename: it is correct but its name implies the wrong event, layer, or ownership.

### 6. Codebase Convention And Reuse Pass

Check whether the implementation fits the repository before judging it in isolation:

- Search for nearby components, composables, utilities, tests, and package scripts that solve the same kind of problem.
- Check existing naming, file structure, import style, state management, error handling, and cleanup patterns in the same package or feature area.
- Inspect installed dependencies and existing wrappers before adding a dependency or writing custom low-level code.
- Prefer the project's shared modules, design system components, composables, utilities, and wrappers over one-off local implementations.
- If a library is already installed, confirm whether it is already used in the codebase and whether local usage patterns differ from upstream examples.
- If the implementation intentionally diverges from local convention, record the reason and make sure the diff or PR body explains it.
- If a new policy, guide, naming scheme, or structured key scheme is introduced, compare the changed call sites against that scheme instead of only checking whether code compiles. Flag names whose domain, ownership, or slot/role does not match their usage.

Run a scope-escalation check: if the user's request names specific surfaces, but the diff changes shared modules, global registration, exported APIs, base components, or cross-package behavior, ask whether the same outcome can be achieved locally. Flag the broader change unless it is necessary and clearly justified by reuse or correctness.

Run a dual-contract check whenever a migration adds a new field, key, helper, adapter, or config while keeping the old one:

- Are both contracts still needed, or can the old one be removed?
- If both remain, which callers own each contract and how long should both exist?
- Do any callers mutate, serialize, compare, or display stale fields from the old contract?
- Does the PR body or code make the transition plan clear enough for reviewers?

Useful search patterns:

```bash
rg -n "similarFunction|similarComponent|libraryName" packages
rg -n "use[A-Z].*|create[A-Z].*|on[A-Z].*" packages/modules/src
rg --files packages | rg "component-or-feature-name"
```

### 7. Responsibility And Naming Pass

Check that names match responsibility:

- `on*` functions should be event handlers for a specific event source.
- `finish*`, `reset*`, `sync*`, and `schedule*` functions should be state commands, not event-specific names.
- Avoid calling an event-specific function from unrelated fallback/cancel paths.
- Avoid one function owning unrelated concerns such as gesture detection, animation state, and click suppression unless the file is already intentionally small.

If a function is called by multiple event sources, prefer a neutral command name.

### 8. State, Flow, And Lifecycle Pass

For any change with meaningful runtime behavior, build a small flow table. Pick columns that match the work instead of forcing an interaction-specific template:

| Scenario | Entry Point | State/Data Changed | Cleanup/Exit | Failure Mode | User/Caller Impact |
| --- | --- | --- | --- | --- | --- |
| Happy path |  |  |  |  |  |
| Empty/null/error input |  |  |  |  |  |
| Repeated/rapid invocation |  |  |  |  |  |
| Cancel/unmount/navigation/retry |  |  |  |  |  |

Then verify:

- Every state, cache, subscription, timer, request, listener, lock, or optimistic update has a clear cleanup or rollback path.
- Repeated invocation does not create duplicate listeners, duplicate requests, stale timers, double commits, or blocked next actions.
- Error, empty, loading, cancellation, and unmount paths leave the system in a coherent state.
- Data transformations preserve sign, units, ordering, identity, precision, and nullability assumptions.
- UI interactions, async flows, service calls, and background side effects are intentionally included or excluded.
- Library behavior is not duplicated unless local code covers a documented gap.

For any changed type, config object, event payload, serialized setting, cache key, or persisted shape:

- Search for stored or external producers that may still emit the old shape, including localStorage/sessionStorage, server responses, fixtures, mocks, imported files, saved user settings, and versioned cache keys.
- Verify old data is normalized, migrated, versioned, or safely ignored before new required fields are read.
- Confirm fallback behavior does not silently display `undefined`, stale data, missing labels, wrong units, or mixed old/new representations.
- If the change intentionally breaks old data, confirm the reset or migration trigger is explicit and tied to the domain key that changed.

When using third-party composables, SDKs, APIs, or framework helpers, inspect their local installed implementation or primary docs for defaults, lifecycle, cleanup, cancellation, retry, and error behavior. Do not rely only on API names.

### 9. Dependency And API Pass

For dependency swaps or new dependencies:

- Confirm the codebase does not already provide a wrapper, composable, utility, or component for the same job.
- Confirm default options match the old behavior.
- Confirm event/value semantics match the old API, including sign, units, thresholds, and lifecycle timing.
- Confirm cleanup behavior, cancellation behavior, and passive listener behavior.
- Remove imports, types, helpers, and comments from the old implementation.

Document non-obvious mappings in code comments only when the mapping is easy to break later.

### 10. PR Readiness Pass

Compare code, PR body, inline comments, and tests:

- PR body must describe the current implementation, not an older iteration.
- Test checklist must only claim checks that actually ran.
- Inline comments should help reviewers understand non-obvious decisions, not justify messy code.
- Tags and feature flag notes should match the actual change.
- If planning docs exist outside the repo, keep them out of Git changes unless explicitly requested.
- If existing PR review comments are present, verify whether each unresolved thread is still valid on the current diff. Mention known unresolved blockers separately from newly found issues.
- If the PR changes a documented convention or migration policy, ensure the body explains final intent and impact rather than listing intermediate naming attempts.

Review new or changed tests as production code:

- Tests should validate behavior or owned contracts, not re-test a third-party library's basic behavior unless the local wrapper changes that behavior.
- Avoid brittle source-code parsing, broad repository scans, or implementation-detail assertions unless they are the narrowest reliable way to protect a real contract.
- Confirm test names and comments describe Given/When/Then behavior and do not claim coverage beyond what is asserted.
- If a test is primarily a policy/enforcement test, verify the policy belongs in the repository and that the failure output is actionable for future authors.

### 11. Reviewer Risk Patterns

Check the current diff against recurring review feedback patterns from prior PRs and high-risk devil's advocate scenarios. Keep these as prompts for focused self-review, not as reasons to over-engineer.

Repository convention, location, and ownership:

- New files should live in the layer that owns the responsibility: app package for app-specific UI, `packages/modules` for shared behavior, and the appropriate `cache`, `local`, or `orchestration` service layer for composables.
- Search for existing components, composables, utilities, wrappers, docs, and layout primitives before adding a new local implementation.
- Avoid putting UI validation, save-flow policy, or view orchestration into raw cache composables.
- If the implementation diverges from an existing pattern, make the reason obvious in code structure or PR explanation.

Component API contract:

- Confirm removed or changed `props`, `emits`, `slots`, `v-model`, event names, and type contracts have no stale call sites.
- Disabled-looking UI must also be disabled in actual interaction semantics: click, keyboard focus, and button/input state.
- Do not rely on `early return` alone when users can still focus or click a control that appears unavailable.
- Documentation and examples must match real components and imports; copy-paste examples should not reference non-existent components.

State, lifecycle, and stale data:

- When a key input changes, old data should not remain visible or feed calculations under the new key.
- `enabled`, unsupported-state, focus, ready, and reconnect paths should all honor the same side-effect guard.
- Watchers should depend on the source that actually changes; avoid watching a derived boolean when same-category transitions need work.
- Subscriptions, timers, listeners, requests, and cached state need cleanup or reset behavior for unmount, retry, reconnect, and repeated invocation.

UI and layout code paths:

- For layout-affecting code, reason through first render, data changes, long/empty text, unsupported/disabled states, and desktop/mobile differences in code.
- Prefer existing layout wrappers and shared UI primitives over ad hoc overflow, height, z-index, or scroll handling.
- DOM measurement should run after a stable render point such as `nextTick` or `requestAnimationFrame`; do not treat arbitrary reactive waits as layout stability.
- Do not start browser capture, device QA, or visual automation unless the user explicitly asks. If visual behavior cannot be verified from code, list it as a manual QA residual risk.

Minimality, dead code, and scope:

- Remove stale imports, listeners, cleanup, props, types, and comments left behind by contract changes.
- Avoid exposing new options or flags when all callers should share one behavior.
- Avoid helper functions, wrappers, or fallback paths whose only purpose is defensive uncertainty.
- Keep docs and guides limited to decisions the codebase owns; do not document design-team-owned rules as engineering policy.

Naming and copy clarity:

- Names should describe domain responsibility, not a nested implementation detail.
- Event-specific names should not be reused for generic state commands or unrelated fallback paths.
- UI copy should prefer direct state descriptions over indirect negative wording when possible.
- Documentation should distinguish required patterns from allowed alternatives.

PR explanation and validation:

- The PR body should describe the final diff, not an earlier iteration.
- Claimed validation must be limited to commands or manual checks actually performed.
- When a behavior depends on a feature flag, unsupported state, or existing shared component behavior, call that out clearly.

High-impact correctness:

- Prioritize anything that can cause outage, data corruption, incorrect orders, incorrect prices, incorrect rankings, or financial/monetary mistakes.
- For market, payment, order, ranking, chart, or financial data, verify units, sign, ordering, rounding, precision, nullability, and whether display-formatted values leak into comparisons or API payloads.
- Avoid floating-point assumptions for money-like values unless the existing domain code already treats the value that way.

Cross-package blast radius:

- If `packages/modules` changes, search desktop, mobile, alphachart, and guest app usage for affected imports, props, emits, types, and runtime assumptions.
- Check whether a shared type or UI contract change needs coordinated updates across app packages.
- If a change is intentionally app-specific, confirm it did not move into shared modules unnecessarily.
- Treat every new export, global registration, base class override, or shared utility as API surface. Verify that each one has a real caller or a necessary framework role.
- When shared constants or config objects gain new required fields, check every object construction path, stored copy, test fixture, mock response, and consumer that spreads or persists the object.
- When a shared field is renamed or replaced, search for both the old and new fields and flag mixed contracts unless an explicit migration period is justified.

Feature flags and rollout:

- For feature-flagged behavior, verify default values, loading/ready state, OFF behavior, unsupported state, and fallback UI.
- Do not assume the flag client is ready on first render.
- Confirm watchers, reconnect paths, and cached state respect the same flag and availability guards as the main path.

User state preservation:

- Decide whether selection, input, filter, tab, scroll, expanded/collapsed state, and modal state should persist across navigation, stock changes, tab changes, reloads, and open/close cycles.
- Do not reset user state unless the product behavior requires it.
- If state should reset, make the reset trigger explicit and tied to the domain key that changed.

API, cache, and async behavior:

- For mutations or save flows, verify cache invalidation, optimistic updates, rollback, stale query behavior, and duplicate-submit protection.
- Confirm query keys include every input that changes the result.
- Ask what happens if an API is slow, fails, returns partial data, or returns after the user navigates away.
- Check rapid repeated actions such as double-click, repeated submit, tab switching, and fast stock/user/account changes.

Accessibility-lite interaction semantics:

- Interactive elements should use correct semantic elements or established button/input components.
- Disabled, readonly, selected, loading, and unavailable states should match keyboard focus, click behavior, aria/state attributes where local patterns use them, and visual styling.
- Clickable `div` or `span` usage needs a concrete reason and should match existing local patterns.

Error, empty, and unavailable states:

- Check empty, error, loading, permission-denied, unsupported, no-data, and offline/slow-network states when the diff touches data-driven UI.
- Avoid silent no-op interactions unless the UI clearly communicates why nothing happened.
- Error messages should be actionable and should not expose implementation details.

Performance and resource use:

- Look for unnecessary recomputation, broad watchers, infinite watch loops, repeated network requests, duplicated subscriptions, and work repeated per render or per row.
- For large lists, charts, order books, rankings, and tables, check whether sorting, mapping, filtering, formatting, and DOM work scale with realistic data sizes.
- Confirm timers, listeners, observers, and subscriptions are cleaned up and not duplicated by repeated entry.

Temporary/debug artifacts:

- Remove console logs, temporary comments, TODOs without owner/date, mock values, debug styles, local-only feature toggles, and commented-out code.

### 12. Validation Pass

Run the narrowest checks that prove the changed surface or validate a finding:

- Lint or format for changed files.
- Type checks scoped or filtered to changed files when full checks are known to fail for unrelated reasons.
- Unit tests or component tests when they exist for the changed area.
- If `$hw.write-pr` will run the mandatory branch-diff lint/format gate later, do not duplicate broad formatting work here unless formatting affects a review finding or the user asks for it now.
- Do not initiate browser capture, device QA, or visual automation unless the user explicitly asks. For UI behavior that needs eyes-on validation, record a manual QA residual risk instead.

Validation must be evidence for behavior, not a replacement for review judgment. A test that only asserts an implementation detail can support a finding, but it does not by itself prove the implementation is minimal, scoped, or reviewer-ready.

When a check fails because of existing unrelated errors, record both:

- The exact command that failed.
- Whether the changed file appears in the failure output.

## Output Format

Use this format when reporting to the user:

```text
PR review result:

Findings:
- [P2] Short title: concrete issue, file/line, why it matters, proposed fix.
- [P3] Short title: concrete issue, file/line, why it matters, proposed fix.
- [P4/P5] Include simplifications likely to generate reviewer feedback, even if not strictly blocking.

Changes made:
- If edits were applied, summarize the finding that caused each edit and the resulting diff.

Validation:
- command: result
- command: result

Commit status:
- Not committed. Waiting for approval.
```

If there are no findings:

```text
PR review result:

No required code changes found.
Optional findings: none.

Residual risks:
- Risk that could not be validated locally.

Validation:
- command: result
```

## Severity Guide

- `P0`: outage, data corruption, security, financial correctness.
- `P1`: likely user-facing regression or broken core behavior.
- `P2`: edge-case regression, unclear state ownership, risky duplicated responsibility.
- `P3`: readability debt likely to generate review feedback.
- `P4`: small simplification or naming improvement.
- `P5`: optional polish.
