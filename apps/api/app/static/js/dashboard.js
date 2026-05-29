const output = document.getElementById("update-output");
const btnBg = document.getElementById("bg-status");
const btnCheck = document.getElementById("check-update");
const btnTrigger = document.getElementById("trigger-update");

function print(data) {
  output.textContent = JSON.stringify(data, null, 2);
}

btnBg?.addEventListener("click", async () => {
  output.textContent = "读取后台检查状态...";
  try {
    const res = await fetch("/api/v1/updates/background-status");
    print(await res.json());
  } catch (err) {
    print({ ok: false, error: String(err) });
  }
});

btnCheck?.addEventListener("click", async () => {
  output.textContent = "检查中...";
  try {
    const res = await fetch("/api/v1/updates/check");
    print(await res.json());
  } catch (err) {
    print({ ok: false, error: String(err) });
  }
});

btnTrigger?.addEventListener("click", async () => {
  output.textContent = "已提交在线更新请求...";
  try {
    const res = await fetch("/api/v1/updates/online", { method: "POST" });
    print(await res.json());
  } catch (err) {
    print({ ok: false, error: String(err) });
  }
});
