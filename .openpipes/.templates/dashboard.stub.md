# 📊 Dashboard - {{targetName}}


```dataviewjs
const folder = dv.current().file.folder;
const alvoName = folder.split("/").pop();
const page = dv.page(`${folder}/${alvoName}.md`);
const baseUrl = page?.targetName ? `https://${page.targetName}` : "";
const services = page.t_services || [];
const closedPorts = page.t_Closed || [];
const filteredPorts = page.t_Filtered || [];

dv.header(2, "🧩 Serviços e Versões");

dv.table(
  ["Porta", "Serviço", "Versão", "TTL", "Fechada", "Filtrada"],
  services.map(item => {
    const parts = item.split(" ");
    const porta = parts[0] || "";
    const servico = parts[1] || "";
    const ttl = parts[4] || "";
    const versao = parts.slice(5).join(" ").trim();
    const isClosed = closedPorts.includes(porta) ? "✅" : "";
    const isFiltered = filteredPorts.includes(porta) ? "✅" : "";
    return [porta, servico, versao, ttl, isClosed, isFiltered];
  })
);

// Parser do httpx.md com deduplicação, filtro de status e limpeza de URL
const httpxPath = `${folder}/httpx.md`;
let httpxFile = app.vault.getAbstractFileByPath(httpxPath);

if (httpxFile) {
  const raw = await app.vault.read(httpxFile);
  const lines = raw.split("\n").filter(l => l.startsWith("|") && !l.includes("---"));

  const urlMap = new Map();

  for (let line of lines.slice(1)) {
    const cols = line.split("|").map(c => c.trim());
    if (cols.length < 7) continue;

    let url = cols[2];
    const status = cols[5];
    const title = cols[6];

    if (!url || !title || title === "-") continue;

    const match = status.match(/^\d+/);
    const statusCode = match ? parseInt(match[0]) : null;
    if (![200, 401, 403].includes(statusCode)) continue;

    // Limpa porta padrão da URL
    url = url.replace(/^http:\/\/([^\/:]+):80\b/, "http://$1");
    url = url.replace(/^https:\/\/([^\/:]+):443\b/, "https://$1");

    // Remove barra final
    url = url.replace(/\/$/, "");

    if (!urlMap.has(url)) {
      urlMap.set(url, title);
    }
  }

  if (urlMap.size > 0) {
    dv.paragraph("## 🔗 [[endpoints.md|Endpoints Mapeados:]]");
    for (let [url, title] of Array.from(urlMap.entries()).sort((a, b) => a[0].localeCompare(b[0]))) {
      dv.paragraph(`- [${url}](${url}) — **${title}**`);
    }
  } else {
    dv.paragraph("⚠️ Nenhum endpoint com status 200, 401 ou 403 e título encontrado no httpx.md.");
  }
} else {
  dv.paragraph("❌ Arquivo httpx.md não encontrado.");
}


dv.header(1, "☑️ Tarefas Pendentes");
dv.taskList(
  dv.pages(`"${folder}"`)
    .where(p => p.file.tasks && p.file.tasks.length > 0)
    .flatMap(p => p.file.tasks)
    .filter(t => !t.completed)
);

```
