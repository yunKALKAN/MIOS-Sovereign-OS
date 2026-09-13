async function loadContracts() {
  const out = document.getElementById("output");
  out.textContent = "Contracts yükleniyor...";

  try {
    const res = await fetch("/contracts");
    const data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = "HATA: " + err.message;
  }
}

async function loadStatus() {
  const out = document.getElementById("output");
  out.textContent = JSON.stringify({
    app: "MUCIZEWORK",
    panel: "ADMIN",
    registry: "LINKED",
    security: "TOKEN_LOCAL_ONLY",
    status: "ONLINE"
  }, null, 2);
}
