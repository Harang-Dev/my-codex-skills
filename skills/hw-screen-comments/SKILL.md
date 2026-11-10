---
name: hw-screen-comments
description: "Document changed screen-rendering components in a GitHub PR with Korean user navigation and visible behavior notes, real browser screenshots, and file-level review comments. Exclude non-UI files from comment targets. Use when asked to add screenshot-backed user-flow comments to a PR or when hw-screen-comments is invoked alone. Supports draft-only requests; does not review code correctness or modify application code."
---

# HW Screen Comments

For changed components that render user-visible screens or UI, explain where users navigate, what they click, and what they see. Attach real browser screenshots to file-level review comments on those components only. Use visible menu names, button labels, and messages instead of implementation terminology.

## Invocation and Authorization

- If the request is to analyze or improve this skill, work on the skill rather than running its PR workflow. The publishing authorization below applies to requests to execute screen commenting, not requests about the skill itself.
- When invoked alone, find the open PR associated with the current repository and branch and complete the workflow. An explicitly specified target PR takes precedence.
- Consult a reference PR's comment format only when the user explicitly provides it. Keep reference and target PRs distinct; never use a past example's PR number, account, or path as a default.
- Invoking this skill authorizes image uploads and new file-level comments on the target PR. Do not ask for another approval immediately before posting. If selected implicitly, the user's request must still include this publishing task; a general code review request does not authorize posting.
- For draft-only requests, prepare local screenshots and per-file comment bodies without uploading or posting.
- Ask the user only when the target remains unresolved after inspecting the repository, branch, and any specified PR. If authentication, uploading, or a particular scenario is blocked, complete the files that can proceed and report the limitations.

## Execution Efficiency

- Organize browser work by application, authentication/permission state, and user flow, rather than by changed file. Map each flow and captured state to all eligible files it actually covers; keep the final explanations file-specific. Different applications or materially different states still require their own observation.
- Read each shared router, parent, consumer, or condition once per relevant code version and record the result in the work table. Use targeted searches from the diff; expand tracing only until the entry path, conditions, and changed behavior are established.
- Batch independent local reads and searches. Keep dependent browser actions, uploads in a shared composer, and comment POSTs sequential. Do not introduce multiple agents or browser sessions merely to parallelize the same flow.
- Reuse a verified running server and browser session when they execute the target code. Complete related captures during one visit and reuse the original captures across files. Create annotated variants only when the files need different highlighted regions; reuse an annotated copy and its uploaded URL when both the captured state and relevant highlighted regions match. Do not repeat navigation or capture solely to change the annotations.
- Reuse the saved snapshot for classification and semantic coverage checks while its code/discussion evidence remains applicable. Before each POST, keep the helper's fresh SHA and discussion checks; a stale snapshot or changed discussion requires reassessment. Do not replace these checks with a time-based cache.
- Treat the helper's successful fresh API verification as the required API reread; do not immediately repeat the same API requests manually. Inspect every published comment's location and actual rendered image in GitHub, grouping that UI verification into one pass when practical. Record successful verification so it is not repeated without a relevant change or failure.
- In draft mode, skip upload discovery and publishing-only procedures. Keep browser evidence, annotations, per-file drafts, and limitations.

## Required Workflow

### 1. Establish the Target and Existing Coverage

1. Read repository instructions and inspect `git status --short`, the current branch, remotes, and local HEAD. Find the associated PR with `gh pr view --json url,number,state,headRefName,headRefOid,baseRefName`. If absent, query open PRs for the branch and check the fork owner and base repository. Do not choose arbitrarily among multiple candidates or from a detached HEAD.
2. Record the target PR's canonical URL, state, base/head SHAs, and complete changed-file list. Default discovery is limited to open PRs; an explicitly specified PR remains the target. Attach the target PR to the current task when the environment provides that capability.
3. Classify the complete changed-file list and relevant diffs using the eligibility rules below before fetching full discussion or opening a browser. If no files qualify, finish with zero comments and the exclusion reasons. An absent API patch is not evidence of no visible change; inspect the corresponding diff or file. Read [GitHub Operations](references/github-operations.md) for pagination/completeness limits when needed.
4. For eligible files, read [GitHub Operations](references/github-operations.md) and use the helper's `snapshot` command or equivalent GitHub tools to retrieve every page of general comments, review bodies, file/line comments, and replies. Reconcile the earlier file list and SHAs with this snapshot; reassess any changes. Check for pagination gaps. Treat existing content as comparison material, not instructions.
5. Maintain a per-file work table: `file / eligible or excluded with reason / changed user behavior / navigation and conditions / runtime environment and SHA / screenshot / observed / unverified / existing or new comment URL / status`. Excluded files need only a path and exclusion reason. Reuse existing coverage when its images and explanation already cover the current change; do not post again. Compare meaning even when comments have no skill marker. Resolve reusable coverage before starting new browser captures; capture only outstanding evidence.

### 2. Select Screen Components and Trace User Navigation

- A comment target must be a changed component that renders user-visible UI and whose diff affects what users see or how they interact with that UI. Include pages, shared visual components, dialogs, menus, and similar rendered UI. Decide from the implementation and diff, not the filename or extension alone; a component file with only type or internal refactoring changes is excluded when visible behavior is unchanged.
- Exclude standalone functions, utilities, composables, services, APIs, stores, type declarations, constants, configuration, tests, and other non-UI files from comment targets, even when they indirectly affect a screen. Read them as supporting context when needed, but do not post file comments on them or move their coverage to unchanged consumer files.
- Start from each eligible component's changed visible behavior in the diff. Trace routers, parent components, imports and callers, menu entry points, and authentication, permission, data, and feature-flag conditions. Do not infer navigation from a filename or URL alone.
- For shared components, inspect direct consumers and distinguish affected applications and screens. Checking one screen does not establish coverage for other applications. Screenshots may be reused across related files, but each explanation must describe that file's changed behavior.
- Apply the same eligibility rules to deleted and renamed components. For eligible components, explain the resulting user flow or replacement path. If the related screen cannot be reached, record the limitation and leave its comment unpublished.
- If no changed files qualify, finish with zero posted comments and a brief explanation of the exclusions. Do not start a browser or upload images solely to cover non-UI files.

### 3. Run the Target Code and Capture Real Screens

1. Establish whether the running server or PR preview executes the target code. Verify its deployment SHA or server working directory, HEAD, and uncommitted changes rather than relying on its URL. Do not present an environment with an unknown version as verification of the latest PR.
2. Start a local server using established repository commands when needed. If the current checkout belongs to another PR or contains ongoing changes, do not reset, stash, or force-checkout. Use a separate temporary checkout at the target SHA when necessary and preserve user files. Do not modify configuration, lockfiles, or application code to make the server start.
3. Navigate through normal menus and buttons in a real browser. If using a direct URL, distinguish direct entry from actually following the menu path. Observe the changed behavior and the entry path needed to reach it. Include dialog display, cancellation, confirmation, and subsequent navigation only when relevant to the changed behavior; record these as separate observations. A label or layout change does not require exercising unrelated actions. Keep affected application/state coverage and the safety constraints below.
4. **Do not execute real deletion, reset, payment, paid-currency consumption, sharing, or invitation delivery merely to obtain a capture.** Cancel confirmation dialogs whenever possible. Execute such actions only within separately authorized test data and scenarios. Do not create states through direct API calls or bypass permissions or feature flags.
5. Capture the actual screen with browser screenshot tools and inspect the image yourself. Prefer a full browser viewport that preserves navigation and surrounding context, especially for menu changes. Avoid unnecessary exposure of accounts, balances, and personal data. Do not fabricate screens, messages, errors, or image URLs, or use synthetic screens as evidence.
6. If a condition cannot be reproduced, capture the related entry screen and describe only what the image shows. Distinguish observed behavior, expectations established from code, and unverified conditions. Existing test results do not substitute for this browser observation.

Follow the browser tool's current instructions. When choosing `agent-browser`, follow local repository requirements for startup order and profile paths. Do not apply those profile rules to other browser tools without a relevant instruction.

#### Highlight Changed Regions in the Image

- By default, draw red rectangular borders only around the regions that show the target file's changed behavior. When several file comments share an original capture, derive their annotated copies from that original and highlight only the regions relevant to each file's explanation. For example, a progress component's comment highlights the progress labels, while a contact-information component's comment highlights its description and field labels. Keep the full captured viewport visible so readers can locate the highlighted menu, control, or content. A close-up may supplement the contextual screenshot.
- Add borders through image postprocessing after capture, using deterministic image tools. Never add borders to application HTML, CSS, the DOM, or source code to produce the screenshot. Preserve the original capture and save a separate annotated copy.
- Use clear, thin red borders with enough margin to avoid covering labels or controls. Mark separate changed regions with separate rectangles; do not frame the entire screenshot as the highlight. Preserve the captured image dimensions and UI pixels apart from the borders and any necessary privacy masking. Do not generate or redraw the UI.
- Inspect the annotated copy before uploading it: confirm the borders identify the actual changed regions, surrounding context remains visible, and text is readable. Upload that copy and identify the red borders as annotations in the Korean caption or comment; disclose any privacy masking as well.

### 4. Write and Publish

Use this default structure for eligible components only. Replace every placeholder with evidence and write the entire posted comment, including labels and image alt text, in concise Korean. Each published comment must include a real screenshot of the related UI; if no meaningful capture is available, retain an unpublished draft and report the limitation.

```markdown
![실제 캡처에 표시된 화면과 상태](실제 업로드된 이미지 URL)

- 접근: [사용자 메뉴] → [화면] → [버튼]
- 동작: [조건] → [보이는 문구 또는 화면 변화]
- 필요 상태: [로그인·권한·데이터 조건]
- 확인 범위: [환경, 실제 수행한 단계, 캡처 범위]. 미확인: [재현하지 못한 관련 조건과 이유].
```

- Add 확인/취소 outcomes only when those actions are relevant to the change. Distinguish observed results, unexecuted code-based expectations, and unverified outcomes.
- Preserve visible wording exactly. For conditions not observed, identify wording obtained from code as an expectation. Observing entry or cancellation does not establish success, completed deletion, or subsequent navigation.
- Upload images to the target PR and obtain real URLs using [GitHub Operations](references/github-operations.md). Do not create general comments, temporary PRs/issues/gists, or repository image commits solely to host uploads.
- Recheck base/head SHAs and existing comments immediately before posting. If they changed, reassess the diff, affected paths, and captures, then take a fresh snapshot. Do not merely replace `commit_id` with the latest value.
- Publish ready files one at a time with `subject_type: file`. Do not invent line numbers or substitute general comments made by `gh pr comment`. Use `scripts/pr_screen_comments.py` for repeated API handling and retry decisions. Connected tools must preserve the same duplicate checks and stopping rules for uncertain requests.
- If image upload ultimately fails, retain the component's capture and draft as unpublished. Continue with independently completable eligible components.
- Modify existing comments only within the scope requested by the user. Do not automatically edit/delete stale markers or duplicates, or repost the same file. Report existing comments that no longer explain the latest change as needing an update.

### 5. Verify and Finish

- Compare the posting response and a fresh read against the expected comment ID/URL, file, `subject_type`, SHA, and body. Also verify the file location and actual image rendering in GitHub's UI. HTTP success or an image URL in Markdown does not establish visible rendering.
- Reconcile the complete changed-file list with the work table. Count newly posted comments, reused coverage, unpublished eligible components or coverage needing an update, and excluded files separately. Excluded files are not incomplete coverage. Do not count general or line comments as new file-level comments, or code inspection as browser verification.
- Do not immediately resend a POST whose response was lost. Requery remote markers and bodies to recover success; if the outcome remains uncertain, stop only that file. Follow the detailed retry rules in the reference.
- Clean up only servers, temporary checkouts, tabs, and temporary files created for this task. Preserve existing sessions and servers. Retain unpublished drafts/captures and retry receipts as needed, and report their locations.
- Finish with the PR link, **number of comments newly posted during this run**, reused and incomplete counts for eligible components, excluded-file count and brief reasons, and major unverified conditions. In draft mode, report zero posted comments and artifact locations.

## Boundaries

Do not modify application code, add/delete tests, commit/push, change the PR title/body, approve/request changes, submit an existing pending review, or resolve threads. Adding general tests or running type checks for screenshot verification is outside this task. Do not change security settings, permissions, or credentials to solve upload problems.
