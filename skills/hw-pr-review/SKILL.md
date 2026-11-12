---
name: hw-pr-review
description: Perform an evidence-first, read-only PR-readiness review of local working-tree changes, a branch diff, or an existing pull request. Use after implementation or refactoring, or whenever the user asks to review a diff, branch, or PR for correctness, regressions, test adequacy, contract/API compatibility, ownership, minimality, lifecycle, data, security, repository conventions, CI/review context, and PR-body drift. Do not use as a fix-or-publish workflow unless the user or invoking workflow explicitly authorizes edits.
---

# HW PR Review

## Goal

Find concrete issues that a careful human reviewer would want fixed before approval. Assess whether the implementation is necessary and fits the repository as well as whether its behavior and contracts are correct. Prefer a small set of well-supported findings over a long speculative checklist.

## Operating Contract

- Default to review-only mode. Read, search, and run non-writing checks; do not edit, stage, commit, push, post comments, or resolve threads.
- Enter fix mode only when the user explicitly requests fixes or an enclosing implementation workflow explicitly authorizes edits. Preserve the original findings, show the resulting diff, and never commit or publish unless separately authorized.
- Review issues introduced or materially worsened by the target change. Include a pre-existing issue only when the change makes it newly reachable or directly relevant; label it clearly.
- Require evidence and an actionable scenario for every finding. Do not report a preference merely because another design is possible.
- Treat passing checks as evidence, not proof of correctness, scope, ownership, minimality, or test adequacy.
- Keep unrelated dirty files untouched and outside the verdict.

## Workflow

### 1. Preflight

1. Resolve the repository root, current branch, requested target, and mode.
2. Read the authoritative instructions that apply to the changed files before inferring conventions from nearby code:
   - every applicable `AGENTS.md`
   - `CONTRIBUTING.md` and `CODEOWNERS`
   - package or feature README/architecture guides
   - package scripts and lint, test, build, and type-check configuration
3. Resolve the comparison base in this order:
   - the user-specified base or revision
   - the existing PR's actual base ref and head SHA
   - a repository-configured integration branch and its merge base; the feature branch's own tracking ref is not automatically its review base
   - the repository default branch as a final fallback
4. When a PR exists, read its title, body, latest reviews, unresolved inline threads, general comments, and failing or pending checks. If any context is unavailable, record that limitation.
5. Reconstruct the review contract from the latest user request, linked requirements, existing behavior, PR context, and repository rules:
   - final intended behavior and behavior that must remain unchanged
   - in-scope and explicitly out-of-scope work
   - affected users, packages, APIs, and data
   - unacceptable regressions
   - validation already performed and remaining unknowns
6. Separate known reviewer feedback from new findings. Do not present an existing comment as an independent discovery.
7. When the repository is AlphaSquare, read [references/alphasquare-risks.md](references/alphasquare-risks.md) and apply only the sections touched by the diff.

### 2. Establish the Exact Review Surface

Define the target before reading implementation bodies:

- **Workspace readiness:** compare the actual merge base with `HEAD`, then include staged, unstaged, and untracked layers.
- **Branch snapshot:** compare the actual merge base with the requested branch head; report local pending layers separately unless the user includes them.
- **PR snapshot:** compare the PR base with the PR head SHA. Do not mix unpushed local changes into the PR verdict, and report whether local `HEAD` matches the PR head.
- **Staged-only:** use only when the user explicitly requests it; still report excluded unstaged and untracked layers.

Mark any fallback base as inferred rather than authoritative.

Resolve base and head refs to immutable SHAs before reading diffs. Read implementation, consumers, and instructions from the reviewed snapshot, not a different checkout. For workspace/staged reviews, retain the selected diff and included untracked contents or their fingerprints so later edits can be detected; status and filenames alone cannot establish an unchanged snapshot. Keep scratch artifacts outside the target worktree.

Collect names and statistics first so the outside-in pass remains meaningful:

```bash
# Local-layer inventory; these layers are not part of a branch/PR snapshot verdict.
git status --short --untracked-files=all
git diff --cached --name-status
git diff --name-status
git ls-files --others --exclude-standard

# Branch/PR snapshot at resolved endpoints.
git diff --name-status --find-renames <merge-base-sha> <head-sha>
git diff --summary <merge-base-sha> <head-sha>

# Combined tracked contents for workspace readiness only.
git diff --name-status HEAD
git diff --name-status <merge-base-sha>
```

Use only the commands relevant to the target and repeat with `--stat` when useful. Prefer `git --no-pager` with `--no-ext-diff --no-textconv --no-color` for patch reads, and NUL-delimited output (`-z`) when processing path lists programmatically. `git diff HEAD` shows the final combined staged and unstaged tracked state; `git diff <merge-base-sha>` adds committed branch changes. Neither includes untracked files, and both read the worktree even if the single revision is pinned. Snapshot diffs require both resolved endpoints.

Create a surface inventory with these layers:

- committed branch or PR changes
- staged changes
- unstaged changes
- untracked files, whose contents must be opened explicitly
- deleted, renamed, case-only renamed, mode-changed, symlink, LFS, binary, submodule, generated, vendored, minified, and lock files
- unrelated dirty files excluded from scope

Classify every changed path as `full review`, `semantic generated review`, `vendor/binary`, or `excluded`, with a reason. Recover truncated output with file-by-file or bounded reads; recheck the target and command result when output is unexpectedly empty. Do not silently skip difficult files. If included content remains unread, use an inconclusive verdict rather than claiming no findings.

Track completion separately from classification: each included item ends as `reviewed` or `blocked` with a reason, never merely assigned or opened. Identify items by layer, status, and old/new path when needed; a staged deletion and untracked recreation of the same path are different items. Reconcile the final inventory against Git, including deletions and small companion files. Report completed/blocked counts and explicit exclusions; counts describe coverage, not correctness.

For large, cross-cutting, delegated, or resumed reviews, read [references/review-orchestration.md](references/review-orchestration.md). It covers bounded review groups, cross-group integration, and safe reuse of earlier review evidence. Small reviews can keep the inventory inline.

### 3. Assess Necessity, Contracts, and Consumers

Start by asking whether the final requirements could be fulfilled with a smaller change to the existing code. Establish the basis for each added responsibility: requested behavior/design, existing behavior to preserve, or a concrete regression caused by the change. Treat the implementation as a proposal to evaluate, not as the assumed solution. Classify the responsibilities as runtime behavior, public API/type, persisted or external data, shared surface, migration/mechanical change, dependency, test, or policy/documentation.

Choose the highest applicable review tier:

| Tier | Typical trigger | Required depth |
| --- | --- | --- |
| Fast | Copy, docs, localized style, fixture, import, or mechanical cleanup with no runtime/shared contract | Read all changed content, verify authority and scope, and run only targeted checks. |
| Standard | Local runtime behavior, component contract, internal API, ordinary bug fix | Inspect direct consumers, relevant neighboring code, behavior scenarios, and test protection. |
| Deep | Shared/exported API, persisted/external data, cross-package change, migration, dependency swap, auth/security, financial correctness, concurrency, or global lifecycle | Search all producers/consumers, map compatibility and migration, inspect full lifecycle, and activate every relevant risk module. |

Escalate when tiers are mixed or uncertainty could hide meaningful impact. Tiers change analysis depth, never surface coverage.

Select risk modules by each responsibility's actual language, framework, runtime, and contract, then union them for related files. Record the applicable repository rule or contract when it affects a finding. Do not impose another project's language checklist or treat a filename extension as proof of framework semantics.

For every added or materially changed surface with consumers, perform an outside-in pass before reading its implementation body:

1. Inspect its consumer-visible name, signature, exported types, documentation, and direct call sites. In files without separate declarations, reveal only the minimum region needed to understand the surface.
2. Record what a reasonable caller would infer about purpose, ownership, inputs, outputs, side effects, errors/nullability, ordering, cleanup, and compatibility.
3. Identify hidden knowledge or friction: surprising defaults, required sequencing, implicit state, unclear errors, non-obvious cleanup, or repeated caller ceremony.
4. After forming that model, read the implementation and compare the inferred and actual contracts.

Use a changed-responsibility ledger only for Deep reviews, responsibility moves, multi-consumer abstractions, stateful runtime changes, migrations, or low-confidence no-finding decisions. Record the element, consumers, responsibility, scope, and `Keep / Inline / Remove / Rename` decision. Do not force a ledger for trivial changes.

### 4. Review Correctness and Design

Read the complete diff for every included layer, the selected final state, every included untracked file, and enough surrounding code to follow changed call paths. Then evaluate these core questions:

- **Necessity and scope:** Which requirement, preserved behavior, or concrete regression justifies each added responsibility? Identify a smaller alternative when one preserves the full contract. Check targeted fixes and moves for unrelated renaming, restructuring, reordering, or formatting; do not demand the fewest lines at the expense of required behavior.
- **Repository fit:** Prefer authoritative repository rules and shared primitives. Compare implementations with the same responsibility, execution triggers, state ownership, and lifecycle, tracing callers and cache updates where relevant. Usage elsewhere, frequency, or a common library alone does not establish suitability; a legacy pattern is not automatically the desired convention.
- **Ownership and complexity:** Does each layer own the policy it implements, and could a local change avoid widening shared/global scope? Does an abstraction provide concrete reuse or a required contract? If synchronization state, watchers, cancellation flags, or guards compensate for the chosen structure, examine whether responsibility placement or execution order can remove that complexity while preserving necessary protection. Report redundant forwarding, fallbacks, state, and stale imports/comments only when a concrete simplification is supported.
- **Behavior and compatibility:** Do happy, boundary, empty, null, error, repeated, and unsupported paths preserve the intended contract? Are old callers, producers, and stored values still compatible?
- **State and lifecycle:** Do requests, watchers, subscriptions, timers, listeners, locks, optimistic updates, and cached state handle retry, cancellation, unmount, navigation, reconnection, and rapid key changes without stale or duplicate effects?
- **Data correctness:** Are identity, ordering, sign, units, precision, rounding, nullability, serialization, and display-versus-domain values preserved?
- **Naming and readability:** Do names describe domain responsibility and event source accurately? Can the code be understood without comments that merely restate it?

For Standard or Deep stateful changes, trace at least the happy path, error/empty path, rapid repeated invocation, and cancellation/unmount/navigation/retry path. Use a small flow table internally when the paths are not obvious.

Route to [references/conditional-review-risks.md](references/conditional-review-risks.md) only when a trigger appears:

| Module | Trigger |
| --- | --- |
| Generated/external artifacts | Generated, vendored, lock, binary, LFS, or submodule changes |
| Persisted data/migration | Storage, serialization, cache keys, external payloads, imports/exports, or old/new shapes |
| Shared/cross-package | Exported or multi-consumer surface, global registration, base primitive, or shared config |
| Security/privacy | Trust boundary, input/HTML, auth/permissions, URLs, cookies/storage, request building, logs/analytics, file transfer, secrets/PII, dependencies, or CI |
| Financial/high-impact data | Money, price, order, payment, ranking, quota, permission, or irreversible operations |
| Feature flags/rollout | Flagged, capability-gated, unsupported, reconnect, or staged-rollout behavior |
| UI/layout/accessibility | Interactive UI, form, dialog, focus/keyboard, disabled/loading/error state, layout, or motion |
| Performance/resources | Hot path, large collection, render/watch loop, polling/retry, network, bundle, timer, observer, or subscription |
| Dependency/framework | Added, removed, upgraded, swapped, or newly used library/framework API |
| Mechanical migration/policy | Broad rename/move/codemod, dual contract, convention, guide, or enforcement test |

### 5. Evaluate Tests and Validation

For every behavior or contract change:

1. Identify the test that protects it.
2. Confirm that the test executes the changed path, asserts owned observable behavior, and would fail if the regression were present.
3. If none exists, decide whether a stable automated regression test should be added based on impact, likelihood, and repository practice.
4. When automation is impractical, specify the exact manual scenario and residual risk.

Review changed tests as production code. Prefer black-box behavior and owned contracts over source parsing, broad scans, excessive mocking, or re-testing a third-party library. Follow repository-specific test naming and structure rules.

Run the narrowest meaningful non-writing checks in review-only mode. Inspect real package scripts and configuration before choosing commands. Run targeted lint, type checks, and tests for Standard/Deep changes; broaden only when shared impact requires it. Do not run auto-fix formatters or any check that mutates the target worktree in review-only mode.

Run `vsc-tsc` only when preparing a PR for creation/update or when the user explicitly requests it. An ordinary review or general verification request does not authorize that command.

For a PR or branch snapshot, run validation against that snapshot in an isolated clean worktree when practical. If local overlays or unrelated dirty files can affect the result, report the contamination and do not attribute the outcome to the snapshot.

Do not initiate browser capture, device QA, or visual automation unless the user explicitly asks. List code-only UI verification as a manual QA residual risk.

For every command, report the exact command, tested SHA/state, and result. Classify failures as introduced by the target, reproduced on the base, flaky/environmental, or unknown because the baseline is unavailable. The presence or absence of a changed filename in output is supporting evidence, not proof of causality. Never claim a check or manual scenario that did not run.

### 6. Check PR Readiness and Report

Compare the final target diff with the PR title, body, comments, feature-flag notes, and validation checklist. Flag stale explanations and unsupported validation claims. Re-evaluate each known unresolved thread against the current diff and keep it separate from new findings.

Before reporting, perform a separate verification pass over candidate findings:

1. Try to disprove each claim with caller guards, normalization, framework/library guarantees, other changed files, and base behavior. Preserve the exact scenario and supporting evidence when it survives; discard a refuted claim with a brief internal reason. Inability to verify is not disproof: route material unknowns to open questions or potential blockers.
2. Verify the location independently of the claim. Match a short verbatim snippet to the exact reviewed file and snapshot, then read its numbered lines. Use the introducing change as the primary anchor and consumers as supporting evidence. Distinguish head/new-side lines from base/old-side deletion lines; do not invent a new-side location for removed code or select a similar snippet in another file. An uncertain anchor requires re-location, not dismissal of a supported issue.
3. Reconcile inventory completion and recheck the selected input contents before declaring readiness. If refs or workspace contents changed, name the frozen snapshot being reported or review the affected changes and consumers again; never combine findings from different states into one current verdict.

Apply this finding gate:

- Every finding must be introduced or materially worsened by the target, anchored in a requirement/API/test/authoritative repository rule, and supported by concrete evidence and an actionable correction.
- For P0-P2, trace a reachable changed path to an observable caller/user/data failure or violated behavioral contract.
- For P3, show the specific maintenance, contract-clarity, or regression-protection gap created by the change and why it matters. For unnecessary complexity, identify what can be removed or simplified and how the required behavior remains covered. A demonstrated runtime failure is not required; a generic preference or demand for more tests is insufficient.
- Cite the narrowest verified file/line and side when needed, demonstrate the scenario or violated contract, and propose a correction and validation direction. If the primary location remains ambiguous, report the limitation without fabricating an inline comment.
- Use `high` confidence for direct or reproducible evidence and `medium` for strong code-path evidence with a remaining runtime assumption.
- Put low-confidence hypotheses under open questions or residual risks, not findings. Highlight a potentially catastrophic unknown as a potential blocker requiring verification.
- Collapse duplicate symptoms into one root-cause finding.
- Put P0-P2 in required findings, P3 in maintainability/test findings, and P4-P5 in suggestions. Include at most three suggestions by default, and omit taste-only nits.

Use this severity guide:

- `P0`: stop-ship exploit, outage, irreversible data loss/corruption, or financial harm with credible reachability.
- `P1`: likely core user-flow regression or serious security/privacy/correctness failure.
- `P2`: concrete edge-case, compatibility, state, lifecycle, or data issue with meaningful impact.
- `P3`: maintainability, contract clarity, or missing-test issue likely to draw review feedback without a demonstrated behavior failure.
- `P4`: small actionable simplification or clarity improvement.
- `P5`: optional polish.

Match the user's language and report in this shape, omitting empty optional sections:

```text
PR review result

Verdict: Ready | Ready with maintainability findings | Changes requested | Inconclusive

Review scope:
- Mode: review-only | fix
- Target/base/head:
- Local HEAD matches reviewed head:
- Tier and activated modules:
- Surface coverage by classification:
- Completion: reviewed / included items; blocked items and reasons; exclusions:
- Snapshot stability / changes during review:
- Truncated/skipped/unrelated files:
- PR/review/CI context:

Required findings:
- [P2][correctness][confidence: high] Title — path:line
  Evidence/Scenario:
  Impact:
  Proposed fix:
  Validation:

Maintainability/test findings:
- [P3][test][confidence: high] ...

Known unresolved feedback:
- ...

Pre-existing issues:
- ...

Potential blockers requiring verification:
- ...

Suggestions:
- [P4] ...

Validation:
- exact command at SHA/state: result

Residual risks / open questions:
- ...

Changes made:
- None. Review-only mode.
```

Use `Changes requested` for P0-P2 or an unresolved blocker, `Ready with maintainability findings` for P3-only results, and `Ready` only when no confirmed findings remain and material validation is complete. Use `Inconclusive` when the target, surface, or critical evidence is incomplete.

When no required changes exist, say `Required findings: none.` If any included content remains unread, do not claim no confirmed findings. Do not declare the PR fully safe or ready when material checks, PR context, or runtime scenarios remain unavailable; describe those residual risks precisely.
