---
name: virtual-scroll-migration
description: Investigate and migrate AlphaSquare Vue lists to the existing shared virtual scrolling implementation while preserving loading, selection, keyboard, scroll, and row lifecycle behavior. Use for targeted virtual-scroll migrations and their review, browser verification, PR, and screen-comment workflow; do not treat every list as a migration target.
---

# AlphaSquare virtual scroll migration

## Scope and evidence

- Follow the requested phase: investigation, pilot, implementation, or coordination. Investigation alone does not authorize application edits, branches, work chats, commits, or publication. Skill creation is a separate authorized artifact.
- Read applicable repository instructions. When choosing a target or precedent, verify candidate lists and comparable implementations against the current main.
- Establish a concrete reason: an accumulating unbounded list, expensive repeated rows, or observed DOM/rendering pressure. Record the actual rendered array and any pagination, slicing, permission caps, or grouping before deciding. A large API result does not imply a large DOM.
- Prefer `@as/composables/utils` → `useVirtualInfiniteList`. Compare the nearest example by data ownership, pagination trigger, scroll owner, state lifetime, and interactions. Similar visual appearance alone is insufficient.

## Before implementation

Trace the renderer, parent and direct consumers, cache/orchestration, row component, and scroll layout. Record:

| Contract | Required evidence |
| --- | --- |
| Rendered data | Exact array after filters/sort/slices; row keys; group headers, inserted banners and loaders; loaded versus rendered count |
| Loading | Query key, page/cursor/offset, termination, fetching guards, next-page failure and recovery, initial viewport fill, refresh, prepend/remove/cache updates |
| Geometry | Actual overflow element, viewport constraint, list offset, header/banner/padding/gap; fixed CSS height versus estimate; image/font/width-dependent size |
| Position | Existing reset events, KeepAlive/unmount behavior, router versus inner scrolling, saved pixel or item anchor, restoration timing |
| Interactions | Selection and select-all across invisible rows, keyboard wrap and scrolling, drag order/indices, menu focus, expansion, media, permissions, row-local state and cleanup |

For cross-cutting work, state scope, preserved behavior, consumers, and unresolved material decisions before editing. Do not add new scroll resets, copy, loading rules, or persistent state without a requirement or concrete regression.

## Implementation decisions

- Keep loading and business state with their existing owners. Virtualization bounds rendered DOM; it does not by itself bound query-cache memory or subscriptions owned by the full dataset.
- Existing hook supports both modes: use real pagination refs and `shouldLoadMore` for a virtual loader-driven list, or set both pagination flags false and retain the existing parent's infinite-scroll trigger. Choose one loading owner. Do not add duplicate loading watchers.
- When switching to a `shouldLoadMore` watcher, check the transition after the query exhausts its retries. If the end is still visible, `hasNextPage` can stay true while `isFetchingNextPage` returns to false, starting a fresh request cycle. Gate automatic loading on the query's next-page error state and verify recovery through the existing refresh or retry path.
- If a required pagination flag is not exported, first consider keeping the current fetch trigger. Expose existing query state only for a concrete consumer need; never invent `hasNextPage` from item count without the API's contract.
- Render a relative spacer with `height: totalSize`, absolute full-width rows, `data-index`, `getVirtualRowStyle`, and `measureRowElement`. Keep loading/empty/permission UI outside or explicitly represented in the virtual row model as appropriate.
- Include actual padding and gap in the measured row footprint. Absolute rows no longer participate in the old flex gap or first/last-child layout. Preserve those semantics explicitly by logical index where needed.
- `estimateSize` is an estimate, not proof of fixed height. Measure rows that can change with content, images, width or expansion. The hook already defers measurement with `nextTick` and checks connectivity; do not duplicate measurement state or modify the hook without a reproduced need.
- Provide stable keys that identify each rendered row. For heterogeneous rows use typed keys such as `date:<date>` and `record:<id>`. Check uniqueness across the full loaded list and distinguish tabs or accounts when the same component is reused. An offset feed can repeat the previous page's last row after an item is prepended on the server. An entity ID or a composite of its fields can identify the entity while still colliding across two rows. If the product requires one row per entity, deduplicate where pages are combined and keep offsets and termination based on the API response. If the existing behavior displays every returned row, preserve both occurrences and give them distinct keys. For a list that appends pages, including the logical index alongside the tab and existing row identity keeps earlier keys stable on append. Recheck identity and measurement reuse if the client can prepend or reorder rows.
- Keep checked/selected/expanded state alive for its required lifetime when a row unmounts. Check the existing row for local state and mount/unmount side effects before moving responsibilities; add only state justified by preserved behavior.
- Keyboard movement must resolve the full logical data index, scroll it into view, then focus the mounted row if required. DOM queries and rendered indices cannot represent offscreen items. `RecentVisit.vue` demonstrates logical lookup plus `scrollToIndex`; it is not a drag implementation.
- Sortable `.toArray()`, DOM order, multi-drag and cross-list drop targets need a compatible data-index contract. Do not silently disable them, narrow selection to mounted rows, or render all rows during a gesture without assessing the actual requirements. Repropose the unit when this exceeds its budget.
- Preserve existing scroll restoration owner and reset events. `useRememberScroll` observes child-list changes, so spacer-size changes, async measurement, and user input during restoration need explicit browser verification. Do not install another restoration watcher speculatively.

## Work units and command center

- For each authorized new virtualization work chat, select **Worktree** when creating the Codex chat. With `create_thread`, use a Git project and `target.environment.type: "worktree"`. Confirm the chat itself opens in the allocated worktree before implementation.
- Fetch `origin/main` before creating the chat and select that ref as its starting state. In the new worktree, verify the starting commit against the fetched `origin/main` SHA before editing. Create the work branch from that SHA using the `hyunwoo/` prefix unless overridden. If setup opens at a stale commit, start the branch from the verified SHA within the new worktree before editing. Record the worktree path and baseline SHA in the command center.
- Group by component directory; combine small independent directories only when the total change and review remain coherent. Count added + deleted lines over the full branch against its actual main merge base, including tests and new files. Use `git diff --numstat <merge-base> HEAD` plus pending tracked/untracked changes while editing. The limit is **300 lines inclusive** per branch.
- Estimate before editing and recount before commit and PR. Do not satisfy the budget through compression, hiding untracked files, or shipping an unusable shared API separately from its required consumer. Repropose a complete unit before exceeding the limit.
- Reuse the existing shared implementation for the pilot unless evidence requires otherwise. If a shared foundation is needed, complete and review a coherent foundation unit first; verify its merge commit is an ancestor of the freshly fetched main before starting dependent work. A published PR is insufficient.
- Create work chats only when the user authorizes that phase. Do not choose a session count from candidate count. First inspect actual remaining scope, estimates, shared-file overlap, active branches, and main integration. Avoid concurrent writes to the same hook/table/cache service.
- Command-center ledger: unit / directory and exact files / baseline main SHA / branch / work chat / owner / added+deleted / dependencies and shared files / review / PR / tested SHA and environment / screenshots and comments / unfinished scenarios / next action. Distinguish proposed, running, blocked, reviewed, PR published, browser verified, commented, and merged.
- Run one representative pilot through review and browser evidence before distributing the rest. Update this skill with observed reusable results, not untested hypotheses; recalculate remaining units afterward.

## Browser validation

- Read repository scripts and use an actual server or preview whose checkout/deployment SHA is verified. Preserve existing sessions. For Agent Browser CLI follow the repository’s startup instructions and use the approved profile for that workspace. Follow the chosen browser tool's own instructions.
- Establish before/after evidence on comparable data, application, viewport, and runtime. Record loaded count, mounted row count, first/last visible item IDs, scrollTop, viewport, and network pagination. Bounded DOM plus intact navigation is the success criterion; do not claim FPS or memory improvements without measuring them.
- Exercise initial empty/loading/error states that exist, fewer-than-viewport results, multiple appended pages, end-of-data, fast down/up scrolling, and revisit at a deep position. Check gaps, overlap, flicker, blank viewports and repeated fetches after mounting and restoration.
- Where the migration introduces automatic range-driven loading, fail a next-page request while the end stays visible. After the configured retries settle, confirm in the network log that no new request cycle starts while idle, then exercise the existing recovery path.
- For mutable offset feeds, append a page whose first row repeats the previous page's last row, using identical fields if the response has no ID. Confirm the number of rows matches the existing display contract. Scroll so the first occurrence leaves the mounted range while the second is still in range, then scroll past both and switch tabs or clear the list. Check that rows leave the DOM as expected and that no links from the previous list remain. Check normal pagination through the last page. Label fixture-based verification separately from live API or socket checks.
- Check narrow/wide widths, image arrival and any expandable content. Change tab/filter/sort/account using real UI, then exercise existing reset/retention behavior. Verify offscreen selection, keyboard boundary/wrap, drag/drop and menus only when present in the target contract.
- Verify mobile web and affected desktop consumers separately for shared code. Capacitor-only pull-to-refresh cannot be validated by desktop mobile emulation: record native device/simulator results separately and leave them unverified if unavailable. Do not change shared PTR behavior to make a capture succeed.
- Record tested SHA, actual steps, observed outcomes, screenshots, and limitations. Screenshots alone do not prove scroll restoration, pagination, or keyboard behavior. Do not fabricate data or bypass permissions; use established mock/test support only within the authorized scenario and label it.

## Review, PR and screen comments

- Self-review every unit. Use `hw-pr-review` for the requested readiness review; use a separate reviewer for high-risk/shared/cross-cutting units under repository rules. Separate introduced regressions, pre-existing issues, quality findings, reviewer feedback and residual risks. Resolve critical issues before publication.
- Run relevant formatting/lint checks; add behavioral regression tests only when they protect meaningful risk. Before test work, read the repository's frontend testing guide with its documented command. Run `vsc-tsc` only during PR preparation or explicit user request.
- For PR publication/update, load `hw-write-pr`, follow the repository template and Korean title/body, check the full branch diff and 300-line budget, and follow the applicable PR approval rules. Keep code edits, commit, push, PR writes and external messages as separate authorized actions. Do not merge without authorization.
- For requested screen comments, load `hw-screen-comments`. It governs real screenshot capture, upload, duplicate checks, file-level comments, and rendered GitHub verification. Comment only changed rendered UI; shared hooks/cache files are supporting evidence, not comment targets. Report unpublished coverage honestly when runtime/auth/native access is unavailable.
- For future virtualization PRs, annotate indentation-only changes from added wrappers in GitHub **Files changed** as a separate line-comment step. Compare the base and head blocks with only leading indentation removed, using the regular PR diff to verify the added-side line numbers. Group consecutive matching lines in one range comment. Split at any change to markup, text, bindings, or handlers, and keep structural changes to the wrapper outside the range. Suggested Korean comment: “가상스크롤 래퍼가 추가되면서 이 구간은 들여쓰기만 바뀌었습니다. 구간 내부 코드는 그대로입니다.”
- Check the current PR head and existing comments before posting each range. Use the new side of the PR diff, skip ranges already covered, and verify the posted link and line range. Track these comments separately from the screenshot-based file comments. Apply this step as part of the upcoming PR workflow.
- Report branch, commit/PR links, exact performed validation and tested SHA, comment URLs/counts, unverified states, line budget and remaining dependencies to the command center. PR publication, browser validation, screen commenting and merge are separate statuses.
