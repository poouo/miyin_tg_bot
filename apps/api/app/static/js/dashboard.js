const securityOutput = document.getElementById("security-output");
const btnCheck = document.getElementById("check-update");
const btnTrigger = document.getElementById("trigger-update");
const btnSaveSecurity = document.getElementById("save-security");

const loginBanEnabled = document.getElementById("login-ban-enabled");
const loginMaxAttempts = document.getElementById("login-max-attempts");
const loginBanMinutes = document.getElementById("login-ban-minutes");

const upgradeFill = document.getElementById("upgrade-fill");
const upgradeStatus = document.getElementById("upgrade-status");

let updatePollTimer = null;

function print(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}

function setUpgradeStatus(progress, text, type = "normal") {
  const safeProgress = Math.max(0, Math.min(100, Number(progress) || 0));
  if (upgradeFill) {
    upgradeFill.style.width = `${safeProgress}%`;
    upgradeFill.classList.remove("success", "failed");
    if (type === "success") upgradeFill.classList.add("success");
    if (type === "failed") upgradeFill.classList.add("failed");
  }
  if (upgradeStatus) {
    upgradeStatus.textContent = `${safeProgress}% - ${text}`;
  }
}

async function pollOnlineUpdateStatus() {
  try {
    const res = await fetch("/api/v1/updates/online-status");
    const data = await res.json();
    if (!data.ok) {
      setUpgradeStatus(0, "Failed to load update status.", "failed");
      stopPolling();
      btnTrigger.disabled = false;
      return;
    }

    const state = data.state || "idle";
    const progress = data.progress || 0;
    const message = data.message || "Working...";

    if (state === "running") {
      setUpgradeStatus(progress, message, "normal");
      btnTrigger.disabled = true;
      return;
    }

    if (state === "success") {
      setUpgradeStatus(100, "Update successful. Refreshing...", "success");
      stopPolling();
      btnTrigger.disabled = false;
      setTimeout(() => window.location.reload(), 1800);
      return;
    }

    if (state === "failed") {
      setUpgradeStatus(progress, "Update failed. Please retry.", "failed");
      stopPolling();
      btnTrigger.disabled = false;
      return;
    }

    setUpgradeStatus(0, "Ready.", "normal");
    stopPolling();
    btnTrigger.disabled = false;
  } catch (err) {
    setUpgradeStatus(0, "Network error while checking update status.", "failed");
    stopPolling();
    btnTrigger.disabled = false;
  }
}

function startPolling() {
  if (updatePollTimer) return;
  updatePollTimer = setInterval(pollOnlineUpdateStatus, 1500);
}

function stopPolling() {
  if (updatePollTimer) {
    clearInterval(updatePollTimer);
    updatePollTimer = null;
  }
}

btnCheck?.addEventListener("click", async () => {
  setUpgradeStatus(0, "Checking update...");
  try {
    const res = await fetch("/api/v1/updates/check");
    const data = await res.json();
    if (!data.ok) {
      setUpgradeStatus(0, "Check update failed.", "failed");
      return;
    }
    if (data.has_update) {
      setUpgradeStatus(0, "Update available. Click Online Update.");
    } else {
      setUpgradeStatus(100, "Already up to date.", "success");
    }
  } catch (err) {
    setUpgradeStatus(0, "Check update failed.", "failed");
  }
});

btnTrigger?.addEventListener("click", async () => {
  btnTrigger.disabled = true;
  setUpgradeStatus(2, "Starting online update...");
  try {
    const res = await fetch("/api/v1/updates/online", { method: "POST" });
    const data = await res.json();
    if (!data.ok) {
      setUpgradeStatus(0, data.message || "Failed to start update.", "failed");
      btnTrigger.disabled = false;
      return;
    }
    startPolling();
    await pollOnlineUpdateStatus();
  } catch (err) {
    setUpgradeStatus(0, "Failed to start update.", "failed");
    btnTrigger.disabled = false;
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

pollOnlineUpdateStatus();

