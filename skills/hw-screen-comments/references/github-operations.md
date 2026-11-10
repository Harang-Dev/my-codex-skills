# GitHub Reading, Attachments, and Publishing

## Target and Snapshot

Discover the PR from the current repository or resolve the user-specified PR, then use the canonical URL returned by GitHub. When given only a number, establish the repository context first. Record reference PRs separately from the target. Verify that the `gh` host and account can access the PR without printing tokens.

Replace example URLs and filenames below with actual lookup results. Keep the run directory outside the repository.

```bash
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/hw-screen-comments"
run_dir="$(mktemp -d "${TMPDIR:-/tmp}/hw-pr-screen-comments.XXXXXX")"
python3 "$skill_dir/scripts/pr_screen_comments.py" snapshot \
  --pr 'https://github.com/OWNER/REPO/pull/NUMBER' \
  --output "$run_dir/snapshot.json"
```

The helper uses only Python's standard library and authenticated `gh`. Its local publishing lock uses `fcntl` on macOS/Linux. `snapshot` is read-only. It saves the PR's base/head SHAs, files, review comments and replies, general comments, and review bodies across all pages. Independent collection reads run with at most four workers, with pagination completed per collection. PR checks before and after the reads remain sequential; a read failure aborts the operation. If PR state changes during the read, it stops for reassessment.

When `files_complete: false`, do not report complete coverage. Investigate GitHub's file-list limit or count mismatch and supplement missing paths using evidence such as a local diff for the same base/head. An absent API `patch` can indicate a binary file or large diff; it does not mean no change. Read `status` and `previous_filename` for deletions and renames. Process retrieved files first without inserting unsupported paths into the snapshot.

The snapshot does not perform semantic analysis. Read bodies, images, and file paths to compare existing user-flow coverage with the current change, including comments without markers. A general comment containing an explanation is not a newly published file-level comment.

## Image Uploads

1. Inspect the real browser capture visually and connect its filename, captured state, and related changed files in the work table.
2. If connected GitHub tools support **attachment-only uploads**, use that capability. Otherwise, use supported file selection, drag-and-drop, or image paste in the target PR's GitHub web composer. Use only APIs supported by the current browser tool.
3. After upload completes, retrieve the actual image URL generated in the composer. Use Preview or the image view to verify the intended capture. Do not invent the URL's host or UUID. Reuse URLs for shared captures.
4. Clear only upload-composer content created for this task. Preserve the user's existing draft comments and reviews. Do not submit a general comment merely to upload an image.
5. If one supported method fails, switch once to another supported method. If still blocked, leave the image and per-file draft unpublished and continue independent files. Do not retry indefinitely, extract cookies/tokens to imitate private upload APIs, or alter security settings.

Some GitHub CLI versions couple `--attach` to general-comment or PR-editing commands. Check local `--help` before relying on support, but do not treat `gh pr comment --attach` as a file-level comment or use `gh pr edit` to insert images. Local paths, `data:`, `blob:`, and temporary server URLs are not valid published image URLs. Even if an uploaded attachment previews correctly, verify it again in the final file comment.

## Per-File Publishing

Save the completed body as a UTF-8 file after semantic duplicate checks and browser observations. Do not interpolate the body into a shell command. Do not run `post` in draft mode.

```bash
python3 "$skill_dir/scripts/pr_screen_comments.py" post \
  --snapshot "$run_dir/snapshot.json" \
  --path 'actual/changed/file.vue' \
  --body-file "$run_dir/file-comment.md"
```

Run `post` serially, one file at a time. Upload images separately. The helper does not verify screenshot authenticity, Korean wording, browser observations, semantic duplicates, or image rendering. There is no additional approval prompt: skill invocation already authorizes this publishing action.

The REST request is `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments` with these four JSON fields:

```json
{
  "body": "Completed Korean body containing actual image URLs",
  "commit_id": "Verified latest PR head SHA",
  "path": "Exact changed-file path in the PR",
  "subject_type": "file"
}
```

Omit `line`, `position`, `side`, and `in_reply_to`. File comments, line comments, replies, and general comments are distinct. If connected GitHub tools do not support this contract, use `gh api --input`. Do not submit existing pending reviews or set review states to approval or changes requested.

The helper:

- Checks that the file was retrieved and that PR state and base/head match the snapshot. Restricting default discovery to open PRs belongs to the earlier target-selection step.
- Repaginates review comments to find existing markers or identical bodies, including the previous path of renamed files. New replies, general comments, or changes to nonempty review bodies require reassessment. Empty review bodies created during comment publishing are ignored.
- Appends an invisible `hw-pr-screen-comments:v1` marker. Its key hashes the host, repository, PR number, and file path. Excluding head from the key prevents unrelated new commits from triggering another comment on the same file.
- Takes a local lock and writes a durable receipt before issuing **exactly one POST**. JSON is passed through `subprocess` arguments and stdin to avoid shell expansion of the body.
- Requeries remote markers to recover from lost responses. Reads created comments again by ID to compare the file, body, SHA, and `subject_type`.

## Result Handling

| Result | Next action |
| --- | --- |
| `created` / `recovered` | Record ID/URL. Check `api_verified` and `pr_unchanged`, then verify images and file location in GitHub's UI. |
| `existing` | Do not repost. If `discussion_changed: true`, take a fresh snapshot and read all discussion/replies before confirming reuse. Reuse sufficient coverage; mark stale or insufficient coverage as needing an update. |
| `duplicates_found` | Report duplicates without further publishing. Do not automatically delete or edit existing comments. |
| `pr_changed` | Reassess code, navigation, and capture impact, then take a fresh snapshot. Do not merely substitute a new SHA. |
| `comments_changed` | Read new discussion, reassess semantic duplicates, and refresh the snapshot. |
| `verification_incomplete` or `pr_unchanged: false` | Distinguish successful publishing from completed verification. Recheck the existing comment and record limitations without another POST. |
| `uncertain` / read failure after POST | Do not resend the same file. Investigate receipts, remote markers, and comment IDs. If unresolved, defer that file and continue others. |
| `unknown_file` / read failure | Investigate target, path, and access. Do not publish to a different PR or substitute a general comment. |

Receipts remain in `${XDG_CACHE_HOME:-$HOME/.cache}/hw-pr-screen-comments` by default. They contain retry metadata such as PR URL, file, SHA, attempt state, and ID, not bodies, captures, or credentials. Preserve uncertain receipts when cleaning up temporary run directories. Use the same state directory when invoking again on the same machine.

The marker and receipt identifiers retain the original `hw-pr-screen-comments` namespace so that renaming the skill preserves duplicate detection and retry history.

A receipt without a visible remote comment does not prove failure. Clear that attempt's receipt and retry only when there is conclusive evidence that the request never reached the server or was rejected, and a complete remote read with the correct account confirms absence. Do not automatically recreate comments deleted after success. The remote API does not provide atomic duplicate prevention for this marker, so do not publish to the same PR concurrently from multiple machines or tools.

Both API reads and visual inspection in GitHub are required after posting. Successful reads, image URL strings, and HTML `img` tags do not prove that image pixels render correctly. The helper intentionally returns `rendering: not_checked`.

## Official Contracts When Needed

- [Create a file-level review comment](https://docs.github.com/en/rest/pulls/comments#create-a-review-comment-for-a-pull-request)
- [PR file lists and pagination limits](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files)
- [Attach files in the browser](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)
- [GitHub CLI attachments](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)

## Validation After Helper Changes

```bash
python3 -B -m unittest discover -s "$skill_dir/scripts" -p 'test_*.py' -v
```

These tests exercise the CLI boundary through a fake `gh` in a temporary directory. They do not make real GitHub requests or verify image uploads or rendering.
