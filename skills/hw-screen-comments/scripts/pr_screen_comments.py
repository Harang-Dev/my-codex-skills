#!/usr/bin/env python3
"""Read PR evidence and publish one resumable file comment using gh (stdlib only)."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


class WorkflowError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("snapshot", help="Read all pages; never posts")
    read.add_argument("--pr", required=True, help="Canonical HTTPS PR URL")
    read.add_argument("--output", required=True, type=Path)
    post = commands.add_parser("post", help="Publish ONE already inspected file")
    post.add_argument("--snapshot", required=True, type=Path)
    post.add_argument("--path", required=True, help="Exact PR filename")
    post.add_argument("--body-file", required=True, type=Path)
    post.add_argument("--state-dir", type=Path, default=Path(
        os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    ) / "hw-pr-screen-comments")
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            result = snapshot(parse_target(args.pr))
            save_json(args.output, result)
            emit({"status": "snapshot", "output": str(args.output.resolve()),
                  "pr": result["pr"], "files_complete": result["files_complete"]})
        else:
            saved = json.loads(args.snapshot.read_text(encoding="utf-8"))
            body = args.body_file.read_text(encoding="utf-8").strip()
            if not body or "<!-- hw-pr-screen-comments:" in body:
                raise WorkflowError("invalid_body", "Supply a nonempty body without a skill marker.")
            target = parse_target(saved["pr"]["url"])
            args.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            # Serialize local publishers for this PR, including renamed files.
            lock_key = digest(target)
            with (args.state_dir / (lock_key + ".lock")).open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                emit(publish(saved, target, args.path, body, args.state_dir))
    except WorkflowError as error:
        emit({"status": error.status, "message": str(error)})
        return 2
    except (OSError, ValueError, KeyError) as error:
        emit({"status": "error", "message": str(error)})
        return 2
    return 0


def snapshot(target):
    before = get_pr(target)
    root = endpoint(target)
    files = api(target, root + "/files?per_page=100", paginate=True)
    comments = api(target, root + "/comments?per_page=100", paginate=True)
    issues = api(target, issue_endpoint(target), paginate=True)
    reviews = api(target, root + "/reviews?per_page=100", paginate=True)
    after = get_pr(target)
    if before != after:
        raise WorkflowError("pr_changed", "PR changed while reading. Inspect the new diff and take a fresh snapshot.")
    return {"schema": 1, "pr": after, "files": files,
            "files_complete": len(files) == after["changed_files"],
            "review_comments": comments, "issue_comments": issues, "reviews": reviews}


def publish(saved, target, path, body, state_dir):
    if saved.get("schema") != 1:
        raise WorkflowError("invalid_snapshot", "Unsupported snapshot schema.")
    item = next((item for item in saved["files"] if item["filename"] == path), None)
    if item is None:
        raise WorkflowError("unknown_file", "Path is not in this PR snapshot.")
    expected = saved["pr"]
    current = get_pr(target)
    if current != expected:
        raise WorkflowError("pr_changed", "PR changed. Recheck code, browser evidence, and snapshot before posting.")
    paths = {path, item.get("previous_filename", path)}
    keys = {file_key(target, name) for name in paths}
    comments = api(target, endpoint(target) + "/comments?per_page=100", paginate=True)
    existing = find_existing(comments, paths, keys, body)
    issues = api(target, issue_endpoint(target), paginate=True)
    reviews = api(target, endpoint(target) + "/reviews?per_page=100", paginate=True)
    discussion_changed = (file_context(comments, paths) != file_context(saved["review_comments"], paths)
                          or discussion_context(issues) != discussion_context(saved["issue_comments"])
                          or discussion_context(reviews) != discussion_context(saved["reviews"]))
    if get_pr(target) != expected:
        raise WorkflowError("pr_changed", "PR changed during the comment check. Reinspect before posting.")
    if existing:
        return existing_result(existing, current, discussion_changed)
    if discussion_changed:
        raise WorkflowError("comments_changed", "PR discussion changed. Read it for existing coverage and refresh the snapshot.")

    key = file_key(target, path)
    receipt = state_dir / (key + ".json")
    # A prior attempt with no visible comment has an unknown outcome, even on a new head.
    if any((state_dir / (old_key + ".json")).exists() for old_key in keys):
        raise WorkflowError("uncertain", "An earlier attempt has no visible remote match. Do not resend; reconcile its receipt and remote result.")
    marker = (f"<!-- hw-pr-screen-comments:v1 key={key} "
              f"head={current['head_sha']} base={current['base_sha']} -->")
    payload = {"body": body + "\n\n" + marker, "commit_id": current["head_sha"],
               "path": path, "subject_type": "file"}
    save_json(receipt, {"pr": current["url"], "path": path, "head_sha": current["head_sha"],
                        "body_sha256": digest(payload["body"]), "status": "attempted"})
    try:
        comment = api(target, endpoint(target) + "/comments", payload=payload)
    except WorkflowError as error:
        # Reconcile once; never repeat the POST automatically.
        try:
            comments = api(target, endpoint(target) + "/comments?per_page=100", paginate=True)
        except WorkflowError:
            raise WorkflowError("uncertain", f"POST and reconciliation failed. Keep receipt {receipt}.") from error
        matches = find_existing(comments, paths, {key}, body)
        if len(matches) != 1:
            raise WorkflowError("uncertain", f"POST outcome unresolved. Keep receipt {receipt}. {error}") from error
        comment = matches[0]
        outcome = "recovered"
    else:
        outcome = "created"
    save_json(receipt, {"pr": current["url"], "path": path, "head_sha": current["head_sha"],
                        "status": outcome, "comment_id": comment["id"],
                        "url": comment.get("html_url")})
    verified = api(target, f"repos/{target['repo']}/pulls/comments/{comment['id']}")
    fields_match = all(verified.get(field) == value for field, value in payload.items())
    after = get_pr(target)
    return {"status": outcome if fields_match else "verification_incomplete",
            "comment": comment_summary(verified), "api_verified": fields_match,
            "pr_unchanged": after == current, "rendering": "not_checked",
            "receipt": str(receipt)}


def find_existing(comments, paths, keys, body):
    result = []
    for comment in comments:
        if comment.get("in_reply_to_id") or comment.get("path") not in paths:
            continue
        text = comment.get("body", "")
        marked = any(f"<!-- hw-pr-screen-comments:v1 key={key} " in text for key in keys)
        same_body = strip_marker(text) == body.strip()
        if marked or same_body:
            result.append(comment)
    return result


def existing_result(comments, current, discussion_changed):
    return {"status": "existing" if len(comments) == 1 else "duplicates_found",
            "comments": [comment_summary(comment) for comment in comments],
            "same_head": all(comment.get("commit_id") == current["head_sha"] for comment in comments),
            "discussion_changed": discussion_changed,
            "rendering": "not_checked",
            "next": "Inspect current coverage, file subject type, and rendered images; do not post again."}


def file_context(comments, paths):
    # Include replies and edits so new discussion is not silently overlooked.
    return {str(comment["id"]): comment for comment in comments if comment.get("path") in paths}


def discussion_context(comments):
    # Standalone file comments can create reviews with empty bodies.
    return {str(comment["id"]): comment["body"] for comment in comments
            if (comment.get("body") or "").strip()}


def strip_marker(body):
    return re.sub(r"\s*<!-- hw-pr-screen-comments:v1 [^\n]*? -->", "", body).strip()


def comment_summary(comment):
    return {key: comment.get(key) for key in
            ("id", "html_url", "path", "subject_type", "commit_id", "body")}


def get_pr(target):
    pr = api(target, endpoint(target))
    return {"url": pr["html_url"], "number": pr["number"], "state": pr["state"],
            "head_sha": pr["head"]["sha"], "base_sha": pr["base"]["sha"],
            "changed_files": pr["changed_files"]}


def endpoint(target):
    return f"repos/{target['repo']}/pulls/{target['number']}"


def issue_endpoint(target):
    return f"repos/{target['repo']}/issues/{target['number']}/comments?per_page=100"


def parse_target(url):
    parsed = urlsplit(url)
    match = re.fullmatch(r"/([^/]+)/([^/]+)/pull/([1-9][0-9]*)/?", parsed.path)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.port or not match):
        raise WorkflowError("invalid_target", "Use the canonical HTTPS PR URL returned by GitHub.")
    return {"host": parsed.hostname.lower(), "repo": f"{match[1]}/{match[2]}",
            "number": int(match[3])}


def file_key(target, path):
    return digest({**target, "path": path})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def api(target, route, payload=None, paginate=False):
    command = ["gh", "api", "--hostname", target["host"], "--method",
               "POST" if payload is not None else "GET", "-H", "Accept: application/vnd.github+json", route]
    if paginate:
        command.extend(["--paginate", "--slurp"])
    if payload is not None:
        command.extend(["--input", "-"])
    try:
        completed = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                                   text=True, capture_output=True, timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise WorkflowError("api_error", str(error)) from error
    if completed.returncode:
        raise WorkflowError("api_error", completed.stderr.strip()[:1000])
    try:
        data = json.loads(completed.stdout)
    except ValueError as error:
        raise WorkflowError("api_error", "GitHub returned invalid JSON.") from error
    return [item for page in data for item in page] if paginate else data


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as output:
        os.chmod(temporary, 0o600)
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
