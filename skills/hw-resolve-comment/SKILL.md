---
name: hw-resolve-comment
description: Address GitHub PR review comments one at a time with reviewer-friendly commit history. Use when the user wants Codex to inspect PR review comments, choose actionable threads, implement fixes, show each fix for user confirmation before committing, create one commit per unrelated review comment or thread, continue comment by comment, and draft or post final replies that include the commit link for each addressed comment. Do not mark GitHub review threads resolved.
---

# HW Resolve Comment

Use this skill to work through GitHub PR review feedback in small, reviewer-friendly commits. The default unit of work is one unresolved actionable review thread or one top-level PR comment. This skill addresses comments with code changes and reviewer replies, but it does not mark GitHub review threads resolved.

The core contract is strict:

- handle one comment or one tightly related comment cluster at a time
- implement only that unit's fix
- show the diff, validation, and proposed commit message
- wait for explicit user confirmation before committing
- create the commit after approval
- only then move to the next comment
- after the queued comments are done, draft reviewer replies that map each addressed comment to its commit link

Do not batch unrelated review comments into one commit.

## Operating Rules

- Do not commit before the user confirms the exact fix.
- Do not push, post replies on GitHub, submit reviews, or mark conversations resolved unless the user explicitly asks.
- Do not resolve GitHub review threads as part of this skill's workflow. If the user explicitly asks to resolve threads, use a separate explicit GitHub operation outside this skill flow after confirming the exact threads.
- Keep git writes serial: stage, commit, then continue. Do not run git write operations in parallel.
- Stage only files needed for the current comment unit.
- If the worktree has unrelated dirty changes, identify them and avoid touching them. If scope is unclear, stop and ask.
- If a comment is ambiguous or conflicts with another comment, stop and ask or propose a response instead of guessing.
- If multiple comments share the same root cause, group them only when the relationship is clear; otherwise ask before grouping.

## Workflow

### 1. Resolve PR Context

Determine the target PR.

- If the user provides a PR URL or number, use it.
- If the user says current PR/current branch, use local context:

```bash
git status --short
git branch --show-current
gh auth status
gh pr view --json number,url,headRefName,baseRefName,title
```

If `gh` is missing or unauthenticated, stop and ask the user to authenticate.

### 2. Read Review Comments

Use thread-aware data when possible. Prefer `gh api graphql` for inline review comments because flat comment reads can lose thread resolution and outdated context.

Collect enough data to know:

- PR number and URL
- thread or comment identity
- author
- body
- file path and line when present
- whether the thread is resolved
- whether the comment is outdated
- surrounding diff or code context

Ignore non-actionable approvals, bot noise, duplicate notifications, and already-resolved comments unless the user asks to inspect them.

### 3. Build The Work Queue

Present a numbered queue before editing:

```text
Review comment queue:
1. [thread/comment id] file:line - one-line requested change
2. [thread/comment id] file:line - one-line requested change

Proposed first item:
- Target:
- Why it is actionable:
- Files likely affected:
```

If the user asked to handle all comments, proceed in queue order after showing the queue. If the queue contains ambiguous or broad items, ask before starting those items.

### 4. Work One Comment Unit

For the current comment unit:

- Re-read the comment and surrounding code.
- Inspect relevant local conventions and nearby usage.
- Implement the smallest fix that satisfies the review feedback without widening scope.
- If the comment asks for explanation rather than code, draft a GitHub reply instead of forcing a code change.
- If the fix reveals a broader bug, stop and explain whether it should remain in this commit or become a separate task.

### 5. Validate The Unit

Run focused checks that are relevant to the current unit.

Examples:

- lint or format for changed files
- targeted unit/component tests
- type checks when the changed contract needs it
- local search proving stale call sites were removed

Do not run broad validation just to fill time. If broad validation is needed, explain why before running it.

### 6. Ask For Confirmation Before Commit

Before any commit, show:

```text
Ready to commit comment <id>:

Addressed feedback:
- reviewer:
- original request:
- resolution:

Changed files:
- path

Validation:
- command: result

Proposed commit:
- <commit message>

Confirm commit / request changes / skip this comment?
```

Wait for explicit confirmation. Do not treat vague acknowledgement as approval if the user asked for a change or expressed uncertainty.

### 7. Commit After Approval

After approval:

```bash
git status --short
git add <only-files-for-this-comment>
git diff --cached --stat
git commit -m "<message>"
```

Commit message guidance:

- Prefer the repository's commit style. If unknown, inspect `git log --oneline -n 2`.
- Keep the message specific to the review comment.
- If the commit addresses multiple related comments, mention the shared behavior rather than listing every comment id.

After committing, record the mapping from comment/thread id to commit SHA and move to the next queued comment.

### 8. Continue Or Stop

After each commit, state:

- completed comment id or thread summary
- commit SHA
- remaining queue count
- next proposed comment

Then continue only with the next queued comment. If the user asks to pause, stop immediately with the remaining queue.

### 9. Draft Final Replies

When all loaded actionable comments are addressed, prepare final reply drafts before ending.

For each addressed comment or thread, include:

- reviewer or thread id
- short summary of what changed
- commit SHA
- commit URL when it can be determined

Use the PR repository URL plus the commit SHA to form commit links when needed:

```text
https://github.com/<owner>/<repo>/commit/<sha>
```

Output format:

```text
Final reply drafts:

Comment <id>:
<Korean reply mentioning the fix and commit link>

Comment <id>:
<Korean reply mentioning the fix and commit link>
```

Do not post these replies automatically. Ask the user whether to post them, edit them, or leave them as drafts. Posting replies must not resolve the GitHub review threads.

## Grouping Rules

Use one commit per unrelated comment.

It is acceptable to group comments into one commit only when:

- they point to the same root cause
- they require the same code change
- splitting them would create artificial or broken intermediate states
- the grouped fix remains easy for reviewers to read

When grouping, say which comments are grouped and why before editing.

## Non-Code Comments

Some comments should not become code commits.

- If a reviewer asks a question, draft an answer and ask before posting.
- If a reviewer suggests a future improvement outside scope, propose deferring it.
- If a comment is already addressed by current code, show the evidence and draft a reply.
- If a comment is stale because the diff changed, verify locally before ignoring it.

## Output Style

Report progress in Korean unless the user asks otherwise.

Keep every update tied to the current comment unit. Avoid summarizing the entire PR repeatedly after the queue is established.
