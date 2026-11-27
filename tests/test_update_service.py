import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from apps.api.app.services import update_service


class UpdateServiceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        patcher = patch.object(update_service, "get_repo_root", return_value=self.repo)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_docker_checks_commit_and_rejects_online_upgrade(self):
        revision = "1" * 40
        latest = "2" * 40
        env = {"MIYIN_DEPLOYMENT": "docker", "MIYIN_BUILD_REVISION": revision, "MIYIN_BUILD_BRANCH": "main"}
        with (
            patch.object(update_service.os, "getenv", side_effect=lambda key, default=None: env.get(key, default)),
            patch.object(update_service, "_run", return_value=(True, f"{latest}\trefs/heads/main")) as git,
            patch.object(update_service.subprocess, "Popen") as spawn,
        ):
            result = update_service.check_update()
            self.assertTrue(result["has_update"])
            self.assertTrue(result["ok"])
            self.assertEqual(result["compare_mode"], "revision")
            self.assertEqual(git.call_args.args[0][-1], "refs/heads/main")
            self.assertEqual(update_service.trigger_online_update()["code"], "update_docker_only")
            spawn.assert_not_called()

    def test_docker_check_falls_back_to_versions_without_git_metadata(self):
        (self.repo / "VERSION").write_text("V1.0.05", encoding="utf-8")
        env = {"MIYIN_DEPLOYMENT": "docker", "MIYIN_BUILD_REVISION": "", "MIYIN_BUILD_BRANCH": ""}
        with (
            patch.object(update_service.os, "getenv", side_effect=lambda key, default=None: env.get(key, default)),
            patch.object(update_service, "urlopen", return_value=io.BytesIO(b"V1.0.06\n")),
            patch.object(update_service, "_run") as git,
        ):
            result = update_service.check_update()
        self.assertTrue(result["has_update"])
        self.assertEqual(result["compare_mode"], "version")
        self.assertEqual(result["remote_version"], "V1.0.06")
        git.assert_not_called()

    def test_git_update_is_detected_when_version_is_unchanged(self):
        def git(repo, *args):
            completed = subprocess.run(
                ["git", "-c", "user.name=Update Test", "-c", "user.email=test@example.invalid", *args],
                cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

        upstream = self.repo / "upstream"
        upstream.mkdir()
        git(upstream, "init", "--initial-branch=main")
        (upstream / "VERSION").write_text("V1.0.05", encoding="utf-8")
        git(upstream, "add", "VERSION")
        git(upstream, "commit", "-m", "initial version")
        git(self.repo, "clone", str(upstream), "deployed")
        deployed = self.repo / "deployed"
        self.assertFalse(update_service._check_git_update(deployed)["has_update"])
        git(upstream, "commit", "--allow-empty", "-m", "update without a version bump")
        result = update_service._check_git_update(deployed)
        self.assertTrue(result["has_update"])
        self.assertEqual(result["remote_version"], "V1.0.05")
        self.assertFalse(result["diverged"])
        git(deployed, "commit", "--allow-empty", "-m", "local change")
        self.assertTrue(update_service._check_git_update(deployed)["diverged"])

    def test_online_update_reports_a_failed_spawn_and_can_be_retried(self):
        script = self.repo / "scripts/linux/local/online_update.sh"
        script.parent.mkdir(parents=True)
        script.touch()
        fake_lock = Mock(LOCK_EX=2, LOCK_NB=4)
        deployment = {"mode": "local", "can_online_update": True}
        with (
            patch.object(update_service, "get_update_deployment", return_value=deployment),
            patch.object(update_service, "fcntl", fake_lock, create=True),
            patch.object(update_service.subprocess, "Popen", side_effect=[OSError("bash unavailable"), Mock(pid=1)]),
        ):
            self.assertFalse(update_service.trigger_online_update()["ok"])
            self.assertEqual(update_service.get_online_update_status()["state"], "failed")
            self.assertTrue(update_service.trigger_online_update()["ok"])
            self.assertEqual(update_service.get_online_update_status()["code"], "update_interrupted")


if __name__ == "__main__":
    unittest.main()
