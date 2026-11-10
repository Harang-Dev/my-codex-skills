"""Exercise the CLI through a fake gh boundary; never contacts GitHub."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("pr_screen_comments.py")
FAKE_GH = r'''
import fcntl, json, os, sys
from pathlib import Path

state_file = Path(os.environ["SCREEN_COMMENT_TEST_STATE"])
lock = state_file.with_suffix(".lock").open("a")
fcntl.flock(lock, fcntl.LOCK_EX)
state = json.loads(state_file.read_text())
args = sys.argv[1:]
route = next(arg for arg in args if arg.startswith("repos/"))
method = args[args.index("--method") + 1]
state["calls"].append({"method": method, "route": route, "args": args})
result = None
error = None
if method == "POST":
    payload = json.load(sys.stdin)
    state["posts"].append(payload)
    if state.get("mode") != "unknown":
        comment = dict(payload, id=800, html_url="https://github.com/example/project/pull/7#discussion_r800")
        state["comments"].append(comment)
        result = comment
    if state.get("mode") in ("unknown", "accepted_then_disconnected"):
        error = "Connection closed; request outcome unknown"
elif route.endswith("/files?per_page=100"):
    result = state["files"]
elif route.endswith("/reviews?per_page=100"):
    result = state.get("reviews", [])
elif "/issues/" in route:
    result = state.get("issues", [])
elif route.endswith("/comments?per_page=100"):
    result = state["comments"]
elif "/pulls/comments/" in route:
    result = next(c for c in state["comments"] if c["id"] == int(route.split("/")[-1]))
    if state.get("mode") == "missing_subject_type":
        result = {k: v for k, v in result.items() if k != "subject_type"}
else:
    state["pr_reads"] = state.get("pr_reads", 0) + 1
    if state.get("change_on_read") == state["pr_reads"]:
        state["pr"]["head"]["sha"] = "c" * 40
    result = state["pr"]
state_file.write_text(json.dumps(state))
fcntl.flock(lock, fcntl.LOCK_UN)
if state.get("fail_route") == route:
    sys.exit("Simulated read failure")
if error:
    print(error, file=sys.stderr)
    sys.exit(1)
if "--paginate" in args:
    if "--slurp" not in args:
        sys.exit("This fixture requires all paginated responses to be slurped")
    result = [result[i:i+100] for i in range(0, len(result), 100)] or [[]]
print(json.dumps(result))
'''


class CommentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pr-screen-comment-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.state_file = self.root / "github.json"
        self.snapshot_file = self.root / "snapshot.json"
        self.body_file = self.root / "body.md"
        self.body_file.write_text("![진입 화면](https://github.com/user-attachments/assets/test-image)\n\n"
                                  "- 접근: 메뉴 → 설정\n- 확인 범위: 진입만 확인. 삭제는 실행하지 않음.\n"
                                  "- 문구: `$(touch forbidden)`과 $HOME은 그대로 전달\n", encoding="utf-8")
        fake = self.root / "gh"
        fake.write_text(f"#!{sys.executable}\n" + FAKE_GH)
        fake.chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.root) + os.pathsep + os.environ.get("PATH", ""),
                    "SCREEN_COMMENT_TEST_STATE": str(self.state_file)}
        self.state_file.write_text(json.dumps({
            "pr": {"html_url": "https://github.com/example/project/pull/7", "number": 7,
                   "state": "open", "head": {"sha": "a" * 40}, "base": {"sha": "b" * 40},
                   "changed_files": 2},
            "files": [{"filename": "src/Menu.vue", "status": "modified"},
                      {"filename": "src/Other.vue", "status": "modified"}],
            "comments": [], "calls": [], "posts": []}))

    def state(self):
        return json.loads(self.state_file.read_text())

    def update(self, **values):
        state = self.state()
        state.update(values)
        self.state_file.write_text(json.dumps(state))

    def run_cli(self, *args, expected_code=0):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                                cwd=self.root, env=self.env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def snapshot(self, expected_code=0):
        return self.run_cli("snapshot", "--pr", "https://github.com/example/project/pull/7",
                            "--output", self.snapshot_file, expected_code=expected_code)

    def post(self, path="src/Menu.vue", expected_code=0):
        return self.run_cli("post", "--snapshot", self.snapshot_file, "--path", path,
                            "--body-file", self.body_file, "--state-dir", self.root / "receipts",
                            expected_code=expected_code)

    def test_snapshot_reads_all_comment_pages_without_writes(self):
        self.update(comments=[{"id": number, "path": "src/Menu.vue", "body": "기존 내용"}
                              for number in range(105)])
        result = self.snapshot()
        saved = json.loads(self.snapshot_file.read_text())
        self.assertTrue(result["files_complete"])
        self.assertEqual(len(saved["review_comments"]), 105)
        self.assertEqual(self.state()["posts"], [])
        self.assertTrue(all(c["method"] == "GET" for c in self.state()["calls"]))

    def test_file_comment_preserves_body_and_repeated_invocation_does_not_repost(self):
        self.snapshot()
        created = self.post()
        self.assertEqual(created["status"], "created")
        self.assertTrue(created["api_verified"])
        self.assertEqual(created["rendering"], "not_checked")
        self.assertEqual(self.post()["status"], "existing")
        posts = self.state()["posts"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(set(posts[0]), {"body", "path", "subject_type", "commit_id"})
        self.assertEqual(posts[0]["subject_type"], "file")
        self.assertEqual(posts[0]["commit_id"], "a" * 40)
        self.assertTrue(posts[0]["body"].startswith(self.body_file.read_text().strip() + "\n\n"))
        self.assertFalse((self.root / "forbidden").exists())

    def test_server_acceptance_followed_by_lost_response_is_recovered_without_retry(self):
        self.snapshot()
        self.update(mode="accepted_then_disconnected")
        self.assertEqual(self.post()["status"], "recovered")
        self.assertEqual(self.post()["status"], "existing")
        self.assertEqual(len(self.state()["posts"]), 1)

    def test_unknown_outcome_survives_restart_and_other_files_can_continue(self):
        self.snapshot()
        self.update(mode="unknown")
        self.assertEqual(self.post(expected_code=2)["status"], "uncertain")
        self.update(mode="normal")
        self.assertEqual(self.post(expected_code=2)["status"], "uncertain")
        self.assertEqual(self.post(path="src/Other.vue")["status"], "created")
        self.assertEqual([p["path"] for p in self.state()["posts"]], ["src/Menu.vue", "src/Other.vue"])

    def test_changed_head_blocks_stale_evidence_before_any_post(self):
        self.snapshot()
        pr = self.state()["pr"]
        pr["head"]["sha"] = "c" * 40
        self.update(pr=pr)
        self.assertEqual(self.post(expected_code=2)["status"], "pr_changed")
        self.assertEqual(self.state()["posts"], [])

    def test_new_file_discussion_requires_reinspection(self):
        self.snapshot()
        self.update(comments=[{"id": 7, "path": "src/Menu.vue", "body": "새로운 논의"}])
        self.assertEqual(self.post(expected_code=2)["status"], "comments_changed")
        self.assertEqual(self.state()["posts"], [])

    def test_new_general_comment_requires_reinspection_before_posting(self):
        self.snapshot()
        self.update(issues=[{"id": 10, "body": "이 사용자 흐름은 이미 위 이미지에서 확인했습니다."}])
        self.assertEqual(self.post(expected_code=2)["status"], "comments_changed")
        self.assertEqual(self.state()["posts"], [])

    def test_new_review_body_requires_reinspection_but_empty_review_does_not(self):
        self.snapshot()
        self.update(reviews=[{"id": 10, "body": "변경된 메뉴 경로와 스크린샷입니다."}])
        self.assertEqual(self.post(expected_code=2)["status"], "comments_changed")
        self.assertEqual(self.state()["posts"], [])
        self.snapshot()
        self.update(reviews=[{"id": 10, "body": "변경된 메뉴 경로와 스크린샷입니다."}, {"id": 11, "body": ""}])
        self.assertEqual(self.post()["status"], "created")

    def test_existing_comment_with_new_reply_requires_coverage_review_without_reposting(self):
        self.snapshot()
        self.post()
        self.snapshot()
        comments = self.state()["comments"]
        comments.append({"id": 900, "path": "src/Menu.vue", "in_reply_to_id": 800,
                         "body": "새 권한 조건에서도 확인되나요?"})
        self.update(comments=comments)
        existing = self.post()
        self.assertEqual(existing["status"], "existing")
        self.assertTrue(existing["discussion_changed"])
        self.assertEqual(len(self.state()["posts"]), 1)

    def test_existing_identical_unmarked_comment_on_last_page_is_not_reposted(self):
        comments = [{"id": number, "path": "other.txt", "body": "다른 파일"} for number in range(100)]
        comments.append({"id": 101, "path": "src/Menu.vue", "body": self.body_file.read_text().strip(),
                         "subject_type": "file", "commit_id": "a" * 40})
        self.update(comments=comments)
        self.snapshot()
        self.assertEqual(self.post()["status"], "existing")
        self.assertEqual(self.state()["posts"], [])

    def test_renamed_file_with_prior_skill_comment_is_not_reposted(self):
        self.snapshot()
        self.post()
        state = self.state()
        state["pr"]["head"]["sha"] = "c" * 40
        state["files"][0] = {"filename": "src/NewMenu.vue", "previous_filename": "src/Menu.vue", "status": "renamed"}
        self.update(**state)
        self.snapshot()
        existing = self.post(path="src/NewMenu.vue")
        self.assertEqual(existing["status"], "existing")
        self.assertFalse(existing["same_head"])
        self.assertEqual(len(self.state()["posts"]), 1)

    def test_missing_file_subject_type_is_not_reported_as_verified(self):
        self.snapshot()
        self.update(mode="missing_subject_type")
        result = self.post()
        self.assertEqual(result["status"], "verification_incomplete")
        self.assertFalse(result["api_verified"])
        self.assertEqual(self.post()["status"], "existing")
        self.assertEqual(len(self.state()["posts"]), 1)

    def test_pr_changing_during_snapshot_does_not_save_mixed_evidence(self):
        self.update(change_on_read=2)
        self.assertEqual(self.snapshot(expected_code=2)["status"], "pr_changed")
        self.assertFalse(self.snapshot_file.exists())

    def test_file_list_shortfall_is_visible_to_the_caller(self):
        pr = self.state()["pr"]
        pr["changed_files"] = 3001
        self.update(pr=pr)
        self.assertFalse(self.snapshot()["files_complete"])

    def test_explicitly_selected_closed_pr_can_receive_a_file_comment(self):
        pr = self.state()["pr"]
        pr["state"] = "closed"
        self.update(pr=pr)
        self.snapshot()
        self.assertEqual(self.post()["status"], "created")

    def test_failed_collection_blocks_snapshot_and_post(self):
        self.snapshot()
        self.update(fail_route="repos/example/project/pulls/7/reviews?per_page=100")
        self.assertEqual(self.post(expected_code=2)["status"], "api_error")
        self.assertEqual(self.state()["posts"], [])
        self.snapshot_file.unlink()
        self.assertEqual(self.snapshot(expected_code=2)["status"], "api_error")
        self.assertFalse(self.snapshot_file.exists())

    def test_head_change_during_post_checks_prevents_post(self):
        self.snapshot()
        self.update(change_on_read=4)
        self.assertEqual(self.post(expected_code=2)["status"], "pr_changed")
        self.assertEqual(self.state()["posts"], [])

    def test_unknown_file_never_posts(self):
        self.snapshot()
        self.assertEqual(self.post(path="absent.vue", expected_code=2)["status"], "unknown_file")
        self.assertEqual(self.state()["posts"], [])


if __name__ == "__main__":
    unittest.main()
