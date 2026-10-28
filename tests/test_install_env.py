import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/linux/init_env.sh"
BASH = shutil.which("bash")
if not BASH and os.name == "nt":
    git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
    if git_bash.is_file():
        BASH = str(git_bash)


@unittest.skipUnless(BASH, "Bash is required to test the Linux installer")
class InstallEnvTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="miyin env test ")
        self.addCleanup(self.temp.cleanup)
        self.app_dir = Path(self.temp.name)
        self.template = self.app_dir / ".env.example"
        self.template.write_text(
            "WEB_PORT=9800\nWEB_ADMIN_PASSWORD=admin\n"
            "WEB_AUTH_SECRET=change_me_to_a_long_random_string\n",
            encoding="utf-8",
        )

    def run_init(self, *, fail_random=False):
        args = [BASH, str(SCRIPT), str(self.app_dir)]
        if fail_random:
            args = [
                BASH, "-c",
                'od() { return 1; }; export -f od; exec bash "$@"',
                "test-init-env", str(SCRIPT), str(self.app_dir),
            ]
        return subprocess.run(args, capture_output=True, text=True, timeout=15)

    def read_env(self):
        return dict(
            line.split("=", 1)
            for line in (self.app_dir / ".env").read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        )

    def test_generates_independent_credentials_and_preserves_template(self):
        original = self.template.read_bytes()
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        values = self.read_env()
        for key in ("WEB_AUTH_SECRET", "WEB_ADMIN_PASSWORD"):
            self.assertRegex(values[key], r"^[0-9a-f]{64}$")
        self.assertNotEqual(values["WEB_AUTH_SECRET"], values["WEB_ADMIN_PASSWORD"])
        self.assertNotIn(values["WEB_AUTH_SECRET"], result.stdout + result.stderr)
        self.assertIn(values["WEB_ADMIN_PASSWORD"], result.stdout)
        self.assertEqual(values["WEB_PORT"], "9800")
        self.assertEqual(self.template.read_bytes(), original)
        self.assertFalse(list(self.app_dir.glob(".env.tmp.*")))
        if os.name != "nt":
            self.assertEqual((self.app_dir / ".env").stat().st_mode & 0o777, 0o600)

    def test_separate_installations_have_different_credentials(self):
        self.assertEqual(self.run_init().returncode, 0)
        first = self.read_env()
        (self.app_dir / ".env").unlink()
        self.assertEqual(self.run_init().returncode, 0)
        second = self.read_env()
        for key in ("WEB_AUTH_SECRET", "WEB_ADMIN_PASSWORD"):
            self.assertNotEqual(first[key], second[key])

    def test_existing_env_is_unchanged_even_without_template_or_random_source(self):
        env_path = self.app_dir / ".env"
        original = b"WEB_AUTH_SECRET=custom-secret\nOTHER_SETTING='a b'\n"
        env_path.write_bytes(original)
        self.template.unlink()
        result = self.run_init(fail_random=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(env_path.read_bytes(), original)
        self.assertNotIn("initial admin password:", result.stdout)

    def test_missing_keys_are_added(self):
        self.template.write_text("WEB_PORT=1234", encoding="utf-8")
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        values = self.read_env()
        self.assertEqual(values["WEB_PORT"], "1234")
        self.assertRegex(values["WEB_AUTH_SECRET"], r"^[0-9a-f]{64}$")
        self.assertRegex(values["WEB_ADMIN_PASSWORD"], r"^[0-9a-f]{64}$")

    def test_random_failure_does_not_publish_default_credentials(self):
        result = self.run_init(fail_random=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.app_dir / ".env").exists())
        self.assertNotIn("initial admin password:", result.stdout)

    def test_missing_template_does_not_create_env(self):
        self.template.unlink()
        result = self.run_init()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.app_dir / ".env").exists())


if __name__ == "__main__":
    unittest.main()
