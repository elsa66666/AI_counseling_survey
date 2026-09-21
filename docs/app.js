const EDGES = ["S→F", "S→P", "F→P", "P→E", "E→S", "E→F", "E→P"];
const FIELD_NAMES = {
  S: "functions.S.label", F: "functions.F.label", F_mode: "functions.F.mode",
  P: "functions.P.label", E: "functions.E.label",
  E_relational_adaptation: "functions.E.relational_adaptation",
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

function edgeCell(edge) {
  const wrap = document.createElement("div");
  wrap.className = "edge";
  wrap.append(badge(edge.presence), document.createElement("br"), badge(edge.validation));
  return wrap;
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
    for (const key of ["S", "F", "F_mode", "P", "E", "E_relational_adaptation"]) tr.append(cell(badge(paper.sfpe[key])));
    for (const edge of EDGES) tr.append(cell(edgeCell(paper.dependencies[edge])));
    tr.append(cell(badge(paper.status)));
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

function evidenceBlock(result) {
  const container = document.createElement("div");
  const votes = document.createElement("div");
  votes.className = "votes";
  votes.textContent = `Votes: ${JSON.stringify(result?.votes ?? {})} · agreement ${Math.round((result?.agreement ?? 0) * 100)}%`;
  container.append(votes);
  for (const item of result?.supporting_evidence ?? []) {
    const block = document.createElement("div");
    block.className = "evidence";
    for (const [label, value] of [[item.auditor, item.evidence], ["Location", item.location], ["Rationale", item.rationale]]) {
      if (!value) continue;
      const p = document.createElement("p");
      const strong = document.createElement("strong");
      strong.textContent = `${label}: `;
      p.append(strong, document.createTextNode(value));
      block.append(p);
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
  const grid = document.createElement("div");
  grid.className = "detail-grid";

  const functions = detailCard("SFPE judgments");
  for (const [label, key] of Object.entries(FIELD_NAMES)) {
    const heading = document.createElement("h4");
    heading.textContent = `${label.replaceAll("_", " ")}: ${paper.sfpe[label]}`;
    functions.append(heading, evidenceBlock(paper.fields[key]));
  }
  grid.append(functions);

  const dependencies = detailCard("Dependencies and validation");
  for (const edge of EDGES) {
    const key = edge.replace("→", "_to_");
    const heading = document.createElement("h4");
    const value = paper.dependencies[edge];
    heading.textContent = `${edge}: ${value.presence} · ${value.validation}`;
    dependencies.append(heading, evidenceBlock(paper.fields[`dependencies.${key}.presence`]));
  }
  grid.append(dependencies);
  root.append(head, grid);
  el("detail").showModal();
}

async function init() {
  const response = await fetch("data/audits.json");
  if (!response.ok) throw new Error(`Could not load audit data: ${response.status}`);
  const payload = await response.json();
  data = payload.papers;
  const summary = payload.summary;
  const stats = [
    [summary.total_papers, "papers"], [summary.unanimous_fields, "unanimous fields"],
    [summary.majority_fields, "majority fields"], [summary.no_majority_fields, "no-majority fields"],
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
