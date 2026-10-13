# Review Orchestration

Read for large, cross-cutting, delegated, or resumed reviews. Use Git and exact source reads to verify coverage and locations; a checklist or another agent's confidence is not evidence of completion. No OCR installation or external review service is required.

## Bound the Review Without Losing Contracts

- Group related implementation, interfaces, producers/consumers, tests, configuration, migrations, and resource variants by responsibility. Shared rule text can reduce repeated context, but is not a substitute for semantic relationships.
- Give each inventory item one primary review owner or batch. Other batches may read it as context; a context read does not complete its own review. Keep deleted files and small companion files in the inventory.
- Size batches so all assigned diffs and necessary context can be read. Split a large group or file into bounded reads with recorded ranges; finish every range. Truncation or tool failure leaves an item blocked until recovered, even if findings already exist elsewhere.
- Carry a compact list of all changed paths and cross-group dependencies into each batch. Keep applicable rules with their source and scope; apply all relevant rules to a mixed-language group.
- After batch reviews, follow contracts across groups: producer to consumer, schema to stored data, export to caller, flag/config to entry point, and implementation to test. Look for missing coordinated changes and assumptions that held only within one group. Collapse duplicates by root cause only after preserving distinct affected consumers.

## Delegation When Useful and Authorized

Use an authorized separate reviewer for broad or high-risk changes; otherwise a sequential self-review is sufficient. Do not require one agent per file or multiple agents for a small change.

Give a reviewer the exact repository and base/head SHAs or frozen workspace artifacts, assigned inventory items, review intent, applicable instructions, related changed paths, and read-only boundary. A reviewer may search beyond the assigned group for evidence. Do not prime an independent discovery pass with the expected bug or preferred conclusion.

Ask for:

- item-by-item completion or a concrete blocked reason;
- candidate findings with requirement/contract, triggering scenario, impact, source snippet and side, and supporting caller evidence;
- counterevidence checked, validation actually run, and unresolved cross-group questions.

The coordinating reviewer reconciles returned items against the original inventory, reads evidence for accepted findings, resolves disagreements with code or reproducible behavior, and performs the cross-group pass. A timed-out reviewer or a clean summary without coverage evidence does not complete its assigned items. Retry or cover them locally; otherwise report the gap.

## Keep Evidence Bound to the Reviewed State

- Pin commit endpoints before review. Record mode, comparison base, head, and included local layers; distinguish a feature branch's tracking ref from its integration base. For a PR, retain the PR base ref/head SHA as well as the resolved comparison base.
- For workspace or staged review, retain the relevant patches and included untracked contents, or content fingerprints, outside the target worktree. Include layer, status, rename paths, and modes in the inventory. Status alone misses edits within an already-modified file.
- Read branch/PR context at the pinned head with `git show <head-sha>:<path>` or a clean isolated checkout. Read old behavior at the comparison base. Local pending fixes or unrelated files must not silently change a snapshot review's evidence.
- Before reuse after interruption or a new commit, compare input contents, relevant requirements/rules, and dependencies. Unchanged file text is insufficient if a consumer, producer, configuration, or contract changed. Reuse only evidence whose assumptions still hold; reopen affected items and validation.
- Before the final report, reconcile added/removed paths and compare the selected input with the recorded state. Re-read changed items and their affected consumers, or report only the named frozen snapshot and disclose the drift. If a coherent snapshot cannot be established, use `Inconclusive`.

## Verify Claims and Locations Separately

For each candidate, retain a compact evidence record: violated expectation, introducing change, reachable scenario, observable impact, strongest counterevidence checked, and exact source anchor. This is working material, not a mandatory extra report section.

Verify facts against all relevant source, not just the local diff. For example, a missing check may be owned by the caller, a removed helper may have moved, and a value's units may be normalized at a boundary. Conversely, a passing test that mocks the changed boundary does not refute a concrete production call path. Do not keep a claim solely because its category is security, concurrency, or compatibility; do not drop one solely because another reviewer could not reproduce it.

Once the claim is supported:

1. Retrieve its actual snippet from the reviewed snapshot; do not reconstruct it from memory or rewrite it to make a match.
2. Confirm the path, symbol, and enclosing context. If the snippet repeats, disambiguate with context before choosing line numbers. A snippet in a sibling implementation file does not validate an anchor on an interface file.
3. Read the narrowest useful numbered range. Anchor regressions caused by deletion to the old path/base side when no suitable surviving changed line exists. Use the selected index/workspace version for staged/workspace findings.
4. If the code is real but the proposed location is wrong, repair the location and recheck the claim there. If the evidence is incomplete, keep the precise uncertainty visible rather than manufacturing a location or silently dropping a serious risk.

Finish when every included item has a completion outcome, cross-group contracts have been reconciled, and every reported finding has passed claim and location verification. More findings or more agents do not compensate for unread scope.
