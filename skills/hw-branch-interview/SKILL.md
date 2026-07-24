---
name: hw-branch-interview
description: Interview the user to build a complete understanding of a git branch or completed branch of work. Use when the user wants Codex to inspect a branch, read the diff and repository context, ask structured questions from basic intent to edge cases, evaluate whether the user's answers are sufficient or inconsistent, and produce a confirmed branch understanding brief without modifying code.
---

# HW Branch Interview

Use this skill to understand a branch deeply through a structured interview. The agent should inspect the branch first, then ask questions that help the user and agent converge on what the branch does, why it exists, how it works, what risks remain, and how to explain it.

This is an interview and understanding workflow, not an implementation workflow.

## Operating Rules

- Do not edit files, commit, push, or create PRs while using this skill unless the user explicitly changes the task.
- Inspect local branch context before asking questions that can be answered from code.
- Ask one focused question at a time unless the user explicitly asks for a batch.
- Start with basic product and intent questions, then move into implementation, data flow, edge cases, validation, and PR explanation.
- After each answer, say whether it is sufficient, incomplete, inconsistent with the diff, or needs evidence.
- Do not accept vague answers such as "just refactor", "cleaner", "better UX", "same as before", or "works normally" without asking for concrete meaning.
- Keep a running understanding and update it as answers arrive.

## Workflow

### 1. Resolve Branch Context

Determine what branch to inspect.

- If the user provides a branch name, compare that branch.
- If the user says current branch, use the current checkout.
- If the branch is already merged or remote-only, fetch/inspect it when available.

Useful commands:

```bash
git status --short
git branch --show-current
git remote -v
base="$(git symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null || echo origin/main)"
git diff --stat "$base"...HEAD
git diff --name-only "$base"...HEAD
git log --oneline "$base"..HEAD
```

If the worktree has unrelated dirty changes, note them and avoid treating them as branch intent unless they are part of the branch.

### 2. Build The Initial Map

Before asking the user, inspect enough code to form a first hypothesis:

- branch name and commit messages
- changed files and package boundaries
- added/removed public APIs, props, emits, types, routes, stores, services, feature flags, and tests
- changed user flows or developer-facing contracts
- obvious risks, TODOs, fallback paths, and validation gaps

Then present:

```text
HYPOTHESIS:
CONFIDENCE:
KNOWN FROM DIFF:
- ...
UNKNOWN:
- ...

Q:
GUESS:
```

### 3. Question Ladder

Ask questions in this order. Skip questions already answered by code or prior user context.

Basic intent:

- What user or developer problem does this branch solve?
- What is the intended final behavior?
- What was wrong, missing, or inefficient before?
- Who is affected: desktop, mobile, alphachart, guest, shared modules, or internal developers?

Scope and non-goals:

- What is intentionally in scope?
- What is intentionally out of scope?
- Which existing behavior must not change?
- Is this a product change, bug fix, refactor, migration, documentation change, or mixed branch?

Implementation model:

- What are the main code paths changed?
- What data enters the feature, how is it transformed, and where does it leave?
- Which state, cache, subscription, route, component contract, or API contract changed?
- Why were these files or layers chosen?

Edge cases and risk:

- What happens on empty, loading, error, unsupported, disabled, permission-denied, slow API, repeated action, navigation, or unmount paths?
- What could regress in another package or shared consumer?
- What feature flags, rollout assumptions, or fallback behavior matter?
- What reviewer question would be hardest to answer?

Validation and evidence:

- What has actually been tested or checked?
- Which commands, manual checks, screenshots, or product scenarios prove it?
- What remains unverified?
- If validation failed or was skipped, why is that acceptable?

PR communication:

- What should the PR title emphasize?
- What should reviewers focus on?
- Which changed files deserve explanation?
- What should be called out as risk, non-goal, or follow-up?

### 4. Answer Evaluation

After each user answer, classify it:

- `Sufficient`: concrete and consistent with the diff.
- `Incomplete`: useful but missing scope, behavior, validation, or evidence.
- `Inconsistent`: conflicts with code, branch diff, or earlier answers.
- `Needs evidence`: plausible, but requires a command, file reference, test, or scenario check.

For incomplete or inconsistent answers:

- state the gap briefly
- cite the relevant file, diff area, or earlier answer when possible
- ask the next narrow question needed to resolve it

### 5. Pressure Test

Before ending, ask at least one pressure-test question. Choose the form that best matches the branch:

- What assumption would make this implementation wrong?
- If a reviewer says this belongs in another layer, what is the defense?
- What user action could break this if it happens twice quickly?
- Which changed shared contract could affect another package?
- What scenario did you not validate?
- What would you remove if the branch had to be half the size?

### 6. Stop Condition

Stop only when:

- intent, outcome, scope, non-goals, affected users/packages, implementation model, risks, validation, and PR explanation are explicit
- the user's answers are consistent with the diff
- at least one pressure-test question has been answered
- another question would only polish wording, not change understanding

If confidence remains low, say exactly what is missing and ask one final reframing question.

### 7. Final Branch Understanding Brief

When ready, produce a concise Korean brief:

```text
# Branch Understanding Brief

- Branch:
- Base:
- Intent:
- Final behavior:
- Affected surfaces:
- Main implementation:
- Data/state flow:
- Scope:
- Non-goals:
- Important risks:
- Validation performed:
- Unverified items:
- Reviewer focus:
- Suggested PR explanation:
- Confidence:
```

End by asking:

```text
Confirm / refine / reject?
```

Do not treat vague confirmation as final if important ambiguity remains.

## Output Style

Use Korean for the interview unless the user asks otherwise.

Keep questions short and concrete. The value of this skill is not asking many questions; it is asking the next question that most improves understanding of the branch.
