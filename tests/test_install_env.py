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

    def run_init(self, *, fail_random=False, repair=False):
        trailing = ["--repair-auth"] if repair else []
        args = [BASH, str(SCRIPT), str(self.app_dir), *trailing]
        if fail_random:
            args = [
                BASH, "-c",
                'od() { return 1; }; export -f od; exec bash "$@"',
                "test-init-env", str(SCRIPT), str(self.app_dir), *trailing,
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

    def test_repairs_only_weak_literal_signing_secret_and_preserves_password(self):
        path = self.app_dir / ".env"
        path.write_text(
            "WEB_PORT=9801\nWEB_AUTH_SECRET=old-key\nWEB_ADMIN_PASSWORD='custom-password' # retained\n",
            encoding="utf-8",
        )
        result = self.run_init(repair=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        values = self.read_env()
        self.assertRegex(values["WEB_AUTH_SECRET"], r"^[0-9a-f]{64}$")
        self.assertEqual(values["WEB_PORT"], "9801")
        self.assertEqual(values["WEB_ADMIN_PASSWORD"], "'custom-password' # retained")
        self.assertNotIn(values["WEB_AUTH_SECRET"], result.stdout + result.stderr)
        self.assertNotIn("initial admin password:", result.stdout)
        self.assertEqual(self.run_init(repair=True, fail_random=True).returncode, 0)

    def test_saved_dashboard_password_does_not_get_rotated(self):
        (self.app_dir / "data").mkdir()
        (self.app_dir / "data" / "admin_password.json").write_text("{}", encoding="utf-8")
        (self.app_dir / ".env").write_text("WEB_AUTH_SECRET=old-key\nWEB_ADMIN_PASSWORD=admin\n", encoding="utf-8")
        result = self.run_init(repair=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(self.read_env()["WEB_AUTH_SECRET"], r"^[0-9a-f]{64}$")
        self.assertEqual(self.read_env()["WEB_ADMIN_PASSWORD"], "admin")

    def test_repair_retains_docker_compose_interpolation(self):
        original = b"WEB_AUTH_SECRET=${SECRET_FROM_ENV}\nWEB_ADMIN_PASSWORD=${PASS_FROM_ENV}\n"
        path = self.app_dir / ".env"
        path.write_bytes(original)
        self.assertEqual(self.run_init(repair=True, fail_random=True).returncode, 0)
        self.assertEqual(path.read_bytes(), original)


@unittest.skipUnless(BASH, "Bash is required to test Docker scripts")
class DockerDeploymentTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="miyin docker test ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.app_dir = self.root / "app"
        self.log = self.root / "commands.txt"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.stub("sudo", 'exec "$@"')
        self.stub("git", 'echo "unexpected Git command" >&2; exit 101')
        self.stub("docker", """
printf '%s\n' "$*" >> "$TEST_COMMAND_LOG"
case "$*" in
  *"config --services") printf 'app\n' ;;
  "compose up --help") printf '%s\n' '  --wait-timeout int' ;;
esac
""")
        self.stub("curl", """
[[ "$1" == "-fsSL" && "$3" == "-o" ]] || exit 102
relative="${2#https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/}"
cat "$TEST_REPO/$relative" > "$4"
""")

    def stub(self, name, body):
        file = self.bin / name
        file.write_text("#!/usr/bin/env bash\n" + body.strip() + "\n", encoding="utf-8", newline="\n")
        file.chmod(0o755)

    def deploy(self, script, *, remote=False, tag="latest"):
        shell = """
if command -v cygpath >/dev/null 2>&1; then
  bin="$(cygpath -u "$1")"; export APP_DIR="$(cygpath -u "$2")"
  export TEST_COMMAND_LOG="$(cygpath -u "$3")" TEST_REPO="$(cygpath -u "$5")"
  script="$(cygpath -u "$4")"
else
  bin="$1"; export APP_DIR="$2" TEST_COMMAND_LOG="$3" TEST_REPO="$5"; script="$4"
fi
export PATH="$bin:$PATH" IMAGE_TAG="$6"
if [[ "$7" == yes ]]; then
  bash <(cat "$script")
else
  bash "$script"
fi
"""
        return subprocess.run(
            [BASH, "-c", shell, "test-docker", str(self.bin), str(self.app_dir), str(self.log),
             str(ROOT / f"scripts/linux/docker/{script}.sh"), str(ROOT), tag, "yes" if remote else "no"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25,
        )

    def test_new_install_pulls_image_without_git_checkout(self):
        result = self.deploy("install")
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.log.read_text(encoding="utf-8")
        self.assertIn("pull ghcr.io/poouo/miyin_tg_bot:latest", commands)
        self.assertIn("up -d --no-build", commands)
        self.assertNotIn("--build app", commands)
        self.assertIn("image: ghcr.io/poouo/miyin_tg_bot:latest", (self.app_dir / "compose.yaml").read_text())
        self.assertTrue((self.app_dir / ".env").is_file())
        self.assertFalse((self.app_dir / ".git").exists())

    def test_remote_upgrade_migrates_legacy_compose_without_changing_its_files(self):
        self.app_dir.mkdir()
        data = self.app_dir / "data"
        data.mkdir()
        (data / "existing.db").write_bytes(b"mock database")
        compose = self.app_dir / "docker-compose.yml"
        compose.write_text("services:\n  app:\n    build: .\n    volumes: ['./data:/app/data']\n", encoding="utf-8")
        original = compose.read_bytes()
        (self.app_dir / "docker-compose.override.yml").write_text("services:\n  app:\n    restart: always\n")
        (self.app_dir / ".env").write_text("WEB_AUTH_SECRET=legacy\nWEB_ADMIN_PASSWORD=custom-password\n")
        result = self.deploy("upgrade", remote=True, tag="1.0.07")
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.log.read_text(encoding="utf-8")
        self.assertIn("pull ghcr.io/poouo/miyin_tg_bot:1.0.07", commands)
        self.assertIn("-f docker-compose.yml -f docker-compose.override.yml -f compose.miyin-image.yaml up -d --no-build", commands)
        self.assertEqual(compose.read_bytes(), original)
        self.assertEqual((data / "existing.db").read_bytes(), b"mock database")
        self.assertIn("WEB_ADMIN_PASSWORD=custom-password", (self.app_dir / ".env").read_text())
        self.assertNotIn("WEB_AUTH_SECRET=legacy", (self.app_dir / ".env").read_text())


if __name__ == "__main__":
    unittest.main()
