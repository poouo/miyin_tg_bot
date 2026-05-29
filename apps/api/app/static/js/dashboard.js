const updateOutput = document.getElementById("update-output");
const securityOutput = document.getElementById("security-output");

const btnBg = document.getElementById("bg-status");
const btnCheck = document.getElementById("check-update");
const btnTrigger = document.getElementById("trigger-update");
const btnSaveSecurity = document.getElementById("save-security");

const loginBanEnabled = document.getElementById("login-ban-enabled");
const loginMaxAttempts = document.getElementById("login-max-attempts");
const loginBanMinutes = document.getElementById("login-ban-minutes");

function print(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}

btnBg?.addEventListener("click", async () => {
  updateOutput.textContent = "loading background status...";
  try {
    const res = await fetch("/api/v1/updates/background-status");
    print(updateOutput, await res.json());
  } catch (err) {
    print(updateOutput, { ok: false, error: String(err) });
  }
});

btnCheck?.addEventListener("click", async () => {
  updateOutput.textContent = "checking...";
  try {
    const res = await fetch("/api/v1/updates/check");
    print(updateOutput, await res.json());
  } catch (err) {
    print(updateOutput, { ok: false, error: String(err) });
  }
});

btnTrigger?.addEventListener("click", async () => {
  updateOutput.textContent = "triggering online update...";
  try {
    const res = await fetch("/api/v1/updates/online", { method: "POST" });
    print(updateOutput, await res.json());
  } catch (err) {
    print(updateOutput, { ok: false, error: String(err) });
  }
});

btnSaveSecurity?.addEventListener("click", async () => {
  securityOutput.textContent = "saving...";
  const payload = {
    login_ban_enabled: Boolean(loginBanEnabled?.checked),
    login_max_attempts: Number(loginMaxAttempts?.value || 5),
    login_ban_minutes: Number(loginBanMinutes?.value || 5),
  };

  try {
    const res = await fetch("/api/v1/security/login", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    print(securityOutput, await res.json());
  } catch (err) {
    print(securityOutput, { ok: false, error: String(err) });
  }
});

