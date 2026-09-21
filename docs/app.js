const EDGES = ["S→F", "S→P", "F→P", "P→E", "E→S", "E→F", "E→P"];
const FIELD_NAMES = {
  S: "functions.S.label", F: "functions.F.label", F_mode: "functions.F.mode",
  P: "functions.P.label", E: "functions.E.label",
  E_relational_adaptation: "functions.E.relational_adaptation",
};
const FIELD_LABELS = {
  S: "S", F: "F", F_mode: "F mode", P: "P", E: "E",
  E_relational_adaptation: "Relational adaptation",
};
let data = [];
let sortKey = "year";
let sortDirection = -1;

const el = id => document.getElementById(id);
const badge = value => {
  const span = document.createElement("span");
  span.className = `badge ${String(value ?? "Unclear").replaceAll(" ", "_")}`;
  span.textContent = value ?? "No majority";
  return span;
};
const cell = content => {
  const td = document.createElement("td");
  if (content instanceof Node) td.append(content); else td.textContent = content ?? "";
  return td;
};

function addOptions(id, values) {
  const select = el(id);
  [...new Set(values.filter(value => value !== null && value !== undefined))].sort().forEach(value => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.append(option);
  });
}

function stackedBadges(first, second) {
  const wrap = document.createElement("div");
  wrap.className = "edge";
  wrap.append(badge(first), document.createElement("br"), badge(second));
  return wrap;
}

function edgeCell(edge) {
  return stackedBadges(edge.presence, edge.validation);
}

function fieldValue(paper, key) {
  if (key in paper.sfpe) return paper.sfpe[key];
  return paper[key] ?? "";
}

function filtered() {
  const query = el("search").value.trim().toLowerCase();
  const values = Object.fromEntries(["year", "S", "F", "P", "E", "validation"].map(id => [id, el(id).value]));
  return data.filter(paper => {
    const haystack = [paper.paper_id, paper.title, paper.authors, ...Object.values(paper.system_names)].join(" ").toLowerCase();
    if (query && !haystack.includes(query)) return false;
    if (values.year && String(paper.year) !== values.year) return false;
    for (const key of ["S", "F", "P", "E"]) if (values[key] && paper.sfpe[key] !== values[key]) return false;
    if (values.validation && !EDGES.some(edge => paper.dependencies[edge].validation === values.validation)) return false;
    return true;
  }).sort((a, b) => {
    const left = String(fieldValue(a, sortKey)).toLowerCase();
    const right = String(fieldValue(b, sortKey)).toLowerCase();
    return left.localeCompare(right, undefined, { numeric: true }) * sortDirection;
  });
}

function render() {
  const papers = filtered();
  const tbody = el("rows");
  tbody.replaceChildren();
  for (const paper of papers) {
    const tr = document.createElement("tr");
    const title = document.createElement("div");
    const link = document.createElement("a");
    link.className = "paper-link";
    link.href = paper.paper_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = paper.title;
    const id = document.createElement("span");
    id.className = "paper-id";
    id.textContent = paper.paper_id;
    title.append(link, id);
    tr.append(cell(title), cell(paper.year));
    tr.append(
      cell(badge(paper.sfpe.S)),
      cell(stackedBadges(paper.sfpe.F, paper.sfpe.F_mode)),
      cell(badge(paper.sfpe.P)),
      cell(badge(paper.sfpe.E)),
      cell(badge(paper.sfpe.E_relational_adaptation)),
    );
    for (const edge of EDGES) tr.append(cell(edgeCell(paper.dependencies[edge])));
    const button = document.createElement("button");
    button.className = "details";
    button.type = "button";
    button.textContent = "Details";
    button.addEventListener("click", () => showDetail(paper));
    tr.append(cell(button));
    tbody.append(tr);
  }
  el("count").textContent = `${papers.length} of ${data.length} papers`;
}

function finalReason(result) {
  if (result?.status === "adjudicated" && result.adjudication?.summary) {
    return result.adjudication.summary;
  }
  const reasons = [...new Set((result?.supporting_evidence ?? [])
    .map(item => item.rationale)
    .filter(Boolean))];
  return reasons.join(" ") || "No final rationale is recorded in the consensus export.";
}

function finalResult(label, result) {
  const block = document.createElement("div");
  block.className = "final-result";
  const heading = document.createElement("h4");
  heading.textContent = label;
  const outcome = document.createElement("div");
  outcome.className = "final-outcome";
  outcome.append(badge(result?.label), document.createTextNode(` ${result?.status ?? "unknown"}`));
  const reason = document.createElement("p");
  reason.textContent = finalReason(result);
  block.append(heading, outcome, reason);
  return block;
}

function evidenceByAuditor(result) {
  const evidence = new Map();
  for (const source of [
    result?.adjudication?.evidence,
    result?.supporting_evidence,
    result?.pre_adjudication?.supporting_evidence,
  ]) {
    for (const item of source ?? []) if (item.auditor) evidence.set(item.auditor, item);
  }
  return evidence;
}

function auditorBlock(result) {
  const container = document.createElement("div");
  const votes = document.createElement("div");
  votes.className = "votes";
  votes.textContent = `Votes: ${JSON.stringify(result?.votes ?? {})} · agreement ${Math.round((result?.agreement ?? 0) * 100)}%`;
  container.append(votes);
  const evidence = evidenceByAuditor(result);
  for (const [auditor, label] of Object.entries(result?.agent_labels ?? {})) {
    const item = evidence.get(auditor);
    const block = document.createElement("div");
    block.className = "evidence";
    const auditorHeading = document.createElement("div");
    auditorHeading.className = "auditor-heading";
    const strong = document.createElement("strong");
    strong.textContent = auditor;
    auditorHeading.append(strong, badge(label ?? "INVALID"));
    block.append(auditorHeading);
    for (const [name, value] of [["Evidence", item?.evidence], ["Location", item?.location],
      ["Rationale", item?.rationale], ["Confidence", item?.confidence]]) {
      if (!value) continue;
      const p = document.createElement("p");
      const key = document.createElement("strong");
      key.textContent = `${name}: `;
      p.append(key, document.createTextNode(value));
      block.append(p);
    }
    if (!item) {
      const note = document.createElement("p");
      note.className = "missing-evidence";
      note.textContent = "This auditor's evidence was not included in the consensus export.";
      block.append(note);
    }
    container.append(block);
  }
  return container;
}

function detailCard(title) {
  const card = document.createElement("section");
  card.className = "detail-card";
  const heading = document.createElement("h3");
  heading.textContent = title;
  card.append(heading);
  return card;
}

function showDetail(paper) {
  const root = el("detail-content");
  root.replaceChildren();
  const head = document.createElement("div");
  head.className = "detail-head";
  const h2 = document.createElement("h2");
  h2.textContent = paper.title;
  const metadata = document.createElement("p");
  metadata.textContent = `${paper.year} · ${paper.authors}`;
  const source = document.createElement("a");
  source.href = paper.paper_url;
  source.target = "_blank";
  source.rel = "noopener noreferrer";
  source.textContent = "Open original paper";
  head.append(h2, metadata, source);
  const finals = detailCard("Final results and rationale");
  for (const [label, key] of Object.entries(FIELD_NAMES)) {
    finals.append(finalResult(FIELD_LABELS[label], paper.fields[key]));
  }
  for (const edge of EDGES) {
    const key = edge.replace("→", "_to_");
    finals.append(
      finalResult(`${edge} presence`, paper.fields[`dependencies.${key}.presence`]),
      finalResult(`${edge} validation`, paper.fields[`dependencies.${key}.validation`]),
    );
  }

  const process = detailCard("Auditor evidence and voting process");
  for (const [label, key] of Object.entries(FIELD_NAMES)) {
    const heading = document.createElement("h4");
    heading.textContent = FIELD_LABELS[label];
    process.append(heading, auditorBlock(paper.fields[key]));
  }
  for (const edge of EDGES) {
    const key = edge.replace("→", "_to_");
    for (const part of ["presence", "validation"]) {
      const heading = document.createElement("h4");
      heading.textContent = `${edge} ${part}`;
      process.append(heading, auditorBlock(paper.fields[`dependencies.${key}.${part}`]));
    }
  }
  root.append(head, finals, process);
  el("detail").showModal();
}

async function init() {
  const response = await fetch(`data/audits.json?v=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Could not load audit data: ${response.status}`);
  const payload = await response.json();
  data = payload.papers;
  const summary = payload.summary;
  const stats = [
    [summary.total_papers, "papers"], [summary.unanimous_fields, "unanimous fields"],
    [summary.majority_fields, "majority fields"], [summary.no_majority_fields, "no-majority fields"],
    [summary.adjudicated_fields ?? 0, "judge-adjudicated fields"],
    [summary.papers_requiring_manual_review, "papers needing review"],
  ];
  for (const [value, label] of stats) {
    const card = document.createElement("div");
    card.className = "stat";
    const strong = document.createElement("strong"); strong.textContent = value;
    const span = document.createElement("span"); span.textContent = label;
    card.append(strong, span); el("stats").append(card);
  }
  addOptions("year", data.map(paper => String(paper.year)).sort((a, b) => b - a));
  for (const key of ["S", "F", "P", "E"]) addOptions(key, data.map(paper => paper.sfpe[key]));
  addOptions("validation", data.flatMap(paper => EDGES.map(edge => paper.dependencies[edge].validation)));
  document.querySelectorAll("input, select").forEach(node => node.addEventListener("input", render));
  el("reset").addEventListener("click", () => { document.querySelectorAll("input, select").forEach(node => node.value = ""); render(); });
  document.querySelectorAll("[data-sort]").forEach(button => button.addEventListener("click", () => {
    const next = button.dataset.sort;
    sortDirection = sortKey === next ? -sortDirection : 1;
    sortKey = next;
    render();
  }));
  render();
}

init().catch(error => { el("count").textContent = error.message; console.error(error); });
