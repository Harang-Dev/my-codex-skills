---
name: hw-write-pr
description: Prepare, validate, draft, and publish or update a GitHub PR for the current branch using git and GitHub CLI. Always run repository-appropriate formatting and lint checks on the full branch diff before drafting, generate a Korean PR title/body from the repository PR template, show the draft for approval, then run the final PR create or update action.
---

# HW Write PR

Use this skill when the user wants Codex to run the PR workflow directly in the current repository: prepare the branch, commit in-scope pending work, run diff-scoped formatting and lint validation, generate a Korean PR draft, pause for approval, then create or update the PR with GitHub CLI.

Do not stop at command suggestions unless the user explicitly asks for draft-only output.

## Operating Model

This workflow uses only standard git and GitHub CLI.

- Required: `git`
- Required for PR writes: authenticated `gh`

## Safety Rules

- Never publish from `main`, `master`, or the detected default branch.
- Treat reruns as normal. Detect existing PRs before deciding whether to create or update.
- Do not silently discard, reset, or overwrite local changes.
- If uncommitted changes are mixed or unrelated to the requested PR, stop and ask which files belong in scope.
- Always show the exact title and body draft before the final PR create/update write.
- Git writes must be serial: stage, commit, push, and PR writes one at a time.
- Before drafting the PR, run formatting and lint checks against the full branch diff and include any resulting fixes in the PR.

## Tool Path Resolution

Do not assume `gh` is available on the current shell `PATH`. Codex worktree shells may omit Homebrew paths even when GitHub CLI is installed.

Resolve GitHub CLI before running any PR command:

1. Try `command -v gh`.
2. If not found, try common install paths:
   - `/opt/homebrew/bin/gh`
   - `/usr/local/bin/gh`
   - `/usr/bin/gh`
3. If still not found, try Homebrew prefixes when `brew` exists:
   - `/opt/homebrew/bin/brew --prefix gh`
   - `/usr/local/bin/brew --prefix gh`
   - Use `<prefix>/bin/gh` if it is executable.
4. Store the resolved executable path as `GH_BIN`.
5. Use `"$GH_BIN"` for every GitHub CLI command, including `--version`, `auth status`, `pr view`, `pr create`, and `pr edit`.
6. Only classify GitHub CLI as missing after all of these checks fail.

## Workflow

1. Resolve repository context.
   - Run `git rev-parse --show-toplevel`.
   - Detect current branch with `git branch --show-current`.
   - Detect default branch from `git symbolic-ref refs/remotes/origin/HEAD --short`; fall back to `origin/main`, `origin/master`, `main`, then `master`.
   - Refuse to continue on the default branch.
   - Determine the comparison base with `git merge-base HEAD <default-ref>` when possible.

2. Validate tools.
   - Check `git --version`.
   - Resolve GitHub CLI as `GH_BIN` using the Tool Path Resolution section.
   - Check `"$GH_BIN" --version`.
   - Check `"$GH_BIN" auth status`.
   - If `GH_BIN` cannot be resolved or is unauthenticated, stop before PR writes and explain the required installation or authentication step.

3. Detect PR mode before publishing.
   - Prefer `"$GH_BIN" pr view --json number,url,state,headRefName,baseRefName,title,body`.
   - If an open PR exists for the branch, the workflow is an update, not a create.
   - If no PR exists, the workflow is a create.

4. Inspect and commit local changes when appropriate.
   - Run `git status --short`.
   - If dirty changes clearly belong to the current task, run `git add` only for the in-scope files, then `git commit`.
   - If the project commit style is unknown, inspect `git log --oneline -n 2` before choosing the message.
   - Use a concise, specific commit message based on the branch purpose and changed files.

5. Run the diff formatting and lint gate.
   - This step is mandatory before PR draft generation.
   - Identify changed files from the full branch diff with `git diff --name-only <base>...HEAD`, plus any uncommitted in-scope files from `git status --short`.
   - Inspect the repository's actual scripts and config before choosing commands:
     - package manager lockfiles and `package.json` scripts
     - ESLint config such as `.eslintrc.*` or `eslint.config.*`
     - Prettier config or Prettier dependencies
     - lint-staged config if present
   - Prefer the repository's existing scripts when they can target the changed files without linting unrelated packages.
   - If scripts only lint broad directories, use direct local binaries through the package manager for the changed files.
   - For JavaScript/TypeScript/Vue changes, run ESLint with fix on the changed lintable files when available, then rerun it without new fixes to confirm.
   - For files covered by Prettier, run Prettier on the changed formattable files when available, then run the relevant ESLint check again because many repositories surface Prettier failures through ESLint.
   - In this repository shape, prefer `yarn prettier --write <changed-files>` for formattable diff files and `yarn eslint --fix <changed-js-ts-vue-files>` for lintable diff files when those binaries exist.
   - If formatting or lint commands change files, inspect `git diff`, stage only in-scope fixes, and commit them before PR draft generation.
   - If a lint or format failure cannot be fixed automatically, stop and report the exact command and failure instead of drafting the PR as ready.
   - Record the commands actually run so the PR body can mention real validation.

6. Push branch when needed.
   - Check whether the current branch has an upstream.
   - If the branch has no upstream, use `git push -u origin <branch>`.
   - If the branch already tracks a remote branch, use `git push` after confirming local commits need publishing.
   - Do not rebase, force push, or change branch history unless the user explicitly asks.

7. Handle conflicts pragmatically.
   - If git reports conflicts, inspect `git status`, `git ls-files -u`, and the conflicted files.
   - Resolve only files relevant to the current branch intent.
   - Remove all conflict markers, stage resolved files, and continue the active git operation.
   - Never continue a merge or rebase without checking the actual git index state.

8. Generate the PR draft.
   - Find the repository PR template in this order:
     - `.github/pull_request_template.md`
     - `.github/PULL_REQUEST_TEMPLATE.md`
     - `.github/PULL_REQUEST_TEMPLATE/*.md`
   - Use the template as the single source of truth for headings and order.
   - If no template exists, use `## Why` and `## Changes`.
   - Write the title and body in Korean unless the user explicitly asks otherwise.
   - Use user-provided docs/specs first. Otherwise derive 내용 from `git diff <base>...HEAD`, `git diff --stat <base>...HEAD`, and relevant changed files.
   - Mention validation actually performed. Do not claim tests that were not run.
   - Leave template sections blank only when the section requires information that cannot be inferred.

9. Pause for approval.
   - Show the exact PR title and body.
   - Include `Harang-Dev` as the assignee in the approval preview.
   - State whether the next write will create a new PR or update an existing PR.
   - Include existing PR number and URL when present.
   - Do not run the final PR write until the user approves.

10. Create or update after approval and assign the PR to `Harang-Dev`.
   - Existing PR: use `"$GH_BIN" pr edit <number> --title <title> --body-file <file> --add-assignee Harang-Dev`. Preserve any existing assignees.
   - New PR: use `"$GH_BIN" pr create --base <base> --head <branch> --title <title> --body-file <file> --assignee Harang-Dev`.
   - Use a temporary body file when the PR body contains multiline Markdown.
   - Re-run `"$GH_BIN" pr view --json number,url,title,body,assignees` after the write to verify the result, including that `Harang-Dev` is assigned.
   - If the PR write succeeds but assignment fails or is missing, report the PR result and assignment failure separately; do not create a duplicate PR or claim assignment succeeded.

11. Report concrete results.
   - Show branch name, final commit SHA, PR number, and PR URL.
   - Say explicitly whether the PR was created or updated.
   - Report whether `Harang-Dev` was confirmed as an assignee.

## Existing PR Rule

If the current branch already has an open PR, do not frame the task as creating a new PR. Refresh branch state, regenerate the PR draft, then update the existing PR after approval.

This avoids duplicate PRs and avoids late failures after a PR already exists.

## Draft Quality Rules

The PR draft must:

- follow the repository PR template exactly for section order
- be written in Korean unless the user asks otherwise
- focus on final intent and impact, not intermediate iterations
- mention concrete user-visible or developer-visible changes
- mention formatting, linting, and tests actually performed, not aspirational checks
- leave sections blank only when the template meaningfully requires user input that cannot be inferred

## Blockers

Stop at the earliest safe point and classify the blocker clearly:

- not inside a git repository
- current branch is the default branch
- missing or unauthenticated GitHub CLI
- mixed uncommitted changes with unclear scope
- unresolved merge/rebase conflict
- no reliable base branch
- user approval required before final PR write
