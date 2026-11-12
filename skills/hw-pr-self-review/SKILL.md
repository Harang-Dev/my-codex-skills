---
name: hw-pr-self-review
description: Leave plain Korean self-review comments on lines in a GitHub PR's Files changed view, explaining non-obvious change reasons for reviewers. Use when asked to add explanatory self-review to a PR, or invoked alone. Supports draft-only requests. Separate from bug-finding reviews and screenshot-backed screen comments.
---

# PR Self-Review

Help a reviewer understand why the code changed. Select lines that need explanation and write short Korean comments using familiar words. Explain the reason or tradeoff, rather than restating the code.

## Scope and authorization

- An explicit request to leave self-review comments, or invocation of this skill alone, authorizes posting explanatory inline comments on the target PR. Do not ask again for approval of those routine comments.
- For a draft-only request, prepare comments and locations without publishing. Creating or improving this skill is not a request to run its publishing workflow.
- Use a user-specified PR. Otherwise find the open PR for the current repository and branch. Ask only if the target remains ambiguous after checking the repository and GitHub.
- This workflow does not authorize source edits, commits, pushes, PR title/body updates, editing others' comments, thread resolution, approval, or requesting changes. Do not submit another pending review.
- This is explanatory self-review, not a full correctness audit. If inspection reveals a concrete defect, report it separately; do not present it as an intentional design or silently fix it.

## Inspect and select

1. Read applicable repository instructions. Establish the PR URL, base/head SHAs, changed files, and local status. Use the remote PR snapshot as the source of truth; do not include unpushed edits in explanations of the published diff.
2. Read the diff, surrounding code, and the callers or contracts needed to explain a choice. Read files from the PR head when the local checkout differs. Inspect API responses, shared components, types, state ownership, or related list refreshes only where relevant.
3. Read all pages of existing review comments and replies, review bodies, and general comments. Reuse existing explanations by meaning, even if their wording or position differs. Do not add a duplicate or edit an existing comment without a request to do so.
4. Choose only changes whose reason is not obvious from the code: a response field needed by another screen, a boundary between shared and domain values, related lists that need refreshing, an order dependency, a compatibility choice, or a deliberate tradeoff. A rename or simple API call usually needs no comment. Do not aim for a fixed count or one comment per file. Explain repeated choices once and name the other affected screen when useful.
5. Anchor each comment to the narrowest relevant line or short range in the current diff. Verify the one-based line and side against that exact head. Deleted lines require the original side. Do not invent positions or substitute a file-level or Conversation comment for a line comment.

## Write in easy Korean

- Usually use one short paragraph of one to three sentences: what requires the choice, then how the code handles it. Add a concrete example only if it helps.
- Prefer familiar words such as “저장된 목록”, “다시 조회”, “선택지”, and “전체 건수”. Keep exact code names only when needed to identify the subject. Avoid unexplained library terms, English abbreviations, and abstract labels.
- Describe the final behavior and actual reason, not the conversation history or abandoned approaches. Do not claim a speculative reason as fact. If the code establishes the effect but not the intent, describe the effect or omit the comment.
- State broad refresh scope or another meaningful tradeoff accurately. Do not imply it is the only possible solution or turn an optional improvement into a defect.
- Do not claim tests or successful user actions that were not performed. Do not copy private account details or credentials into comments.

Example of a useful explanation:

> 멤버 목록과 함께 전체 건수도 돌려줍니다. 한 번에 받은 멤버 수로는 마지막 페이지를 알 수 없어서, 서버가 준 전체 건수로 페이지 수를 계산합니다.

Avoid merely saying “전체 건수를 반환하도록 수정했습니다.”

## Publish and verify

- Prefer connected GitHub tools that support inline review comments. If unavailable or inaccessible, use authenticated GitHub CLI. Resolve `gh` on PATH or common install paths, including `/opt/homebrew/bin/gh`, and retain its resolved path.
- Prepare structured arguments or a UTF-8 JSON payload file. Do not interpolate comment bodies into shell code.
- Immediately before publishing, recheck the PR head and discussion for changed code or new equivalent explanations. Reassess affected comments if either changed.
- Submit the selected comments as one `COMMENT` review when supported, anchored to the verified head. Use line/side fields, not guessed diff positions. Keep the review body brief and explanatory; never use `APPROVE` or `REQUEST_CHANGES` for this task.
- If a write fails or its outcome is unclear, read the remote reviews/comments before retrying or switching tools. Compare head, path, line, and body to avoid double posting. If success remains uncertain, report the unresolved result instead of repeating the write.
- Read back every posted comment and verify its body, path, line/side, head SHA, and review state. Some review-specific endpoints omit line fields; use the PR's review-comment list or individual comment endpoint when needed. Verify publication rather than assuming a saved pending review is visible.
- Finish with the review or PR link, count of newly posted comments, and any drafts or blockers. If all useful explanations already exist, report zero new comments. Keep the code and existing discussion unchanged.
