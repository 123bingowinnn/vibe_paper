const translations = {
  en: {
    eyebrow: "Agent-Native Local Paper Workspace",
    "button.generateContext": "Generate Context",
    "button.saveFile": "Save File",
    "button.compilePaper": "Compile Paper",
    "button.refreshPreview": "Refresh Preview",
    "button.openFormalPdf": "Open Formal PDF",
    "button.reload": "Reload",
    "status.project": "Project",
    "status.activeFile": "Active file",
    "status.paperStatus": "Paper status",
    "status.paperNotInitialized": "Paper workspace not initialized",
    "status.waitingForScan": "Waiting for project scan",
    "panel.projectFiles": "Project Files",
    "panel.sourceEditor": "Source Editor",
    "panel.pdfPreview": "PDF Preview",
    "panel.buildLog": "Build Log",
    "common.none": "None",
    "common.metadataOnly": "metadata only",
    "common.directory": "[D]",
    "common.file": "[F]",
    "editor.noFileSelected": "No file selected",
    "editor.readOnly": "Read-only",
    "editor.unsavedChanges": "Unsaved changes",
    "editor.saved": "Saved",
    "editor.ready": "Ready",
    "editor.reloaded": "Reloaded after external edit",
    "editor.externalChange": "External change detected",
    "preview.notLoaded": "Preview not loaded",
    "preview.synced": "Preview synced",
    "preview.refreshed": "Preview refreshed",
    "log.idle": "Idle",
    "log.generatingContext": "Generating project snapshot...",
    "log.contextUpdated": "Project snapshot updated",
    "log.compiling": "Compiling...",
    "log.buildSucceeded": "Build succeeded",
    "log.buildFailed": "Build failed",
    "log.runningLatex": "Running LaTeX build...\n",
    "log.noOutput": "No log output.",
    "log.bootstrapFailed": "Failed to bootstrap app",
    "lang.toggle": "\u4e2d\u6587",
  },
  zh: {
    eyebrow: "\u9762\u5411 Agent \u7684\u672c\u5730\u8bba\u6587\u5de5\u4f5c\u53f0",
    "button.generateContext": "\u751f\u6210\u4e0a\u4e0b\u6587",
    "button.saveFile": "\u4fdd\u5b58\u6587\u4ef6",
    "button.compilePaper": "\u7f16\u8bd1\u8bba\u6587",
    "button.refreshPreview": "\u5237\u65b0\u9884\u89c8",
    "button.openFormalPdf": "\u6253\u5f00\u6b63\u5f0f PDF",
    "button.reload": "\u91cd\u65b0\u52a0\u8f7d",
    "status.project": "\u9879\u76ee",
    "status.activeFile": "\u5f53\u524d\u6587\u4ef6",
    "status.paperStatus": "\u8bba\u6587\u72b6\u6001",
    "status.paperNotInitialized": "\u8bba\u6587\u5de5\u4f5c\u533a\u5c1a\u672a\u521d\u59cb\u5316",
    "status.waitingForScan": "\u7b49\u5f85\u9879\u76ee\u626b\u63cf",
    "panel.projectFiles": "\u9879\u76ee\u6587\u4ef6",
    "panel.sourceEditor": "\u6e90\u7801\u7f16\u8f91\u533a",
    "panel.pdfPreview": "PDF \u9884\u89c8",
    "panel.buildLog": "\u7f16\u8bd1\u65e5\u5fd7",
    "common.none": "\u65e0",
    "common.metadataOnly": "\u4ec5\u8bb0\u5f55\u5143\u6570\u636e",
    "common.directory": "[\u76ee\u5f55]",
    "common.file": "[\u6587\u4ef6]",
    "editor.noFileSelected": "\u5c1a\u672a\u9009\u62e9\u6587\u4ef6",
    "editor.readOnly": "\u53ea\u8bfb",
    "editor.unsavedChanges": "\u6709\u672a\u4fdd\u5b58\u6539\u52a8",
    "editor.saved": "\u5df2\u4fdd\u5b58",
    "editor.ready": "\u5c31\u7eea",
    "editor.reloaded": "\u68c0\u6d4b\u5230\u5916\u90e8\u4fee\u6539\uff0c\u5df2\u91cd\u65b0\u52a0\u8f7d",
    "editor.externalChange": "\u68c0\u6d4b\u5230\u5916\u90e8\u4fee\u6539",
    "preview.notLoaded": "\u9884\u89c8\u5c1a\u672a\u52a0\u8f7d",
    "preview.synced": "\u9884\u89c8\u5df2\u540c\u6b65",
    "preview.refreshed": "\u9884\u89c8\u5df2\u5237\u65b0",
    "log.idle": "\u7a7a\u95f2",
    "log.generatingContext": "\u6b63\u5728\u751f\u6210\u9879\u76ee\u5feb\u7167...",
    "log.contextUpdated": "\u9879\u76ee\u5feb\u7167\u5df2\u66f4\u65b0",
    "log.compiling": "\u6b63\u5728\u7f16\u8bd1...",
    "log.buildSucceeded": "\u7f16\u8bd1\u6210\u529f",
    "log.buildFailed": "\u7f16\u8bd1\u5931\u8d25",
    "log.runningLatex": "\u6b63\u5728\u8fd0\u884c LaTeX \u7f16\u8bd1...\n",
    "log.noOutput": "\u6ca1\u6709\u53ef\u663e\u793a\u7684\u65e5\u5fd7\u8f93\u51fa\u3002",
    "log.bootstrapFailed": "\u5e94\u7528\u521d\u59cb\u5316\u5931\u8d25",
    "lang.toggle": "EN",
  },
};

const state = {
  activePath: null,
  activeMtime: null,
  previewMtime: null,
  dirty: false,
  editable: true,
  pollingHandle: null,
  language: localStorage.getItem("vibe-paper-language") || "en",
  lastTree: [],
};

const treeEl = document.getElementById("file-tree");
const editorEl = document.getElementById("editor");
const buildLogEl = document.getElementById("build-log");
const pdfFrameEl = document.getElementById("pdf-frame");
const editorStatusEl = document.getElementById("editor-status");
const previewStatusEl = document.getElementById("preview-status");
const logStatusEl = document.getElementById("log-status");
const activeFileValueEl = document.getElementById("active-file-value");
const paperStatusValueEl = document.getElementById("paper-status-value");
const projectRootValueEl = document.getElementById("project-root-value");
const toggleLanguageEl = document.getElementById("toggle-language");

document.getElementById("save-file").addEventListener("click", saveActiveFile);
document.getElementById("compile-paper").addEventListener("click", compilePaper);
document.getElementById("regenerate-context").addEventListener("click", regenerateContext);
document.getElementById("refresh-preview").addEventListener("click", refreshPreview);
document.getElementById("reload-tree").addEventListener("click", loadBootstrap);
document.getElementById("open-formal-pdf").addEventListener("click", () => {
  window.open(`/pdf/formal?ts=${Date.now()}`, "_blank");
});
toggleLanguageEl.addEventListener("click", toggleLanguage);

editorEl.addEventListener("input", () => {
  state.dirty = true;
  updateEditorStatus();
});

window.addEventListener("keydown", async (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
    event.preventDefault();
    await saveActiveFile();
  }
});

function t(key) {
  return translations[state.language][key] || translations.en[key] || key;
}

function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  toggleLanguageEl.textContent = t("lang.toggle");
  if (!state.activePath) {
    activeFileValueEl.textContent = t("common.none");
  }
  if (!paperStatusValueEl.dataset.hasValue) {
    paperStatusValueEl.textContent = t("status.waitingForScan");
  }
  if (!editorStatusEl.dataset.hasValue) {
    editorStatusEl.textContent = t("editor.noFileSelected");
  }
  if (!previewStatusEl.dataset.hasValue) {
    previewStatusEl.textContent = t("preview.notLoaded");
  }
  if (!logStatusEl.dataset.hasValue) {
    logStatusEl.textContent = t("log.idle");
  }
  renderTree(state.lastTree || []);
}

function toggleLanguage() {
  state.language = state.language === "en" ? "zh" : "en";
  localStorage.setItem("vibe-paper-language", state.language);
  applyLanguage();
  updateEditorStatus();
}

async function loadBootstrap() {
  const response = await fetch("/api/bootstrap");
  const payload = await response.json();
  projectRootValueEl.textContent = payload.projectName;
  state.lastTree = payload.tree || [];
  renderTree(state.lastTree);
  setPaperStatus(payload.paperStatus || []);
  if (payload.defaultFile) {
    await openFile(payload.defaultFile);
  } else {
    activeFileValueEl.textContent = t("common.none");
  }
  refreshPreview();
  if (state.pollingHandle) {
    clearInterval(state.pollingHandle);
  }
  state.pollingHandle = setInterval(pollState, 3000);
}

function renderTree(nodes) {
  treeEl.innerHTML = "";
  const container = document.createElement("div");
  nodes.forEach((node) => container.appendChild(renderNode(node)));
  treeEl.appendChild(container);
}

function renderNode(node) {
  const wrapper = document.createElement("div");
  wrapper.className = "tree-node";

  const row = document.createElement("div");
  row.className = `tree-row ${node.highlight || ""}`.trim();
  if (state.activePath === node.path) {
    row.classList.add("active");
  }
  row.innerHTML = `
    <span>${node.type === "dir" ? t("common.directory") : t("common.file")}</span>
    <span>${node.name}</span>
    ${node.metadataOnly ? `<span class="tree-meta">${t("common.metadataOnly")}</span>` : ""}
  `;
  row.addEventListener("click", async () => {
    if (node.type === "file") {
      await openFile(node.path);
    }
  });
  wrapper.appendChild(row);

  if (node.children && node.children.length > 0) {
    const children = document.createElement("div");
    children.className = "tree-children";
    node.children.forEach((child) => children.appendChild(renderNode(child)));
    wrapper.appendChild(children);
  }
  return wrapper;
}

async function openFile(path) {
  const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  const payload = await response.json();
  state.activePath = payload.path;
  state.activeMtime = payload.mtime;
  state.dirty = false;
  state.editable = payload.editable;
  editorEl.value = payload.content || "";
  editorEl.disabled = !payload.editable;
  activeFileValueEl.textContent = payload.path;
  updateEditorStatus(payload.message || "");
  await loadTreeOnly();
}

async function loadTreeOnly() {
  const response = await fetch("/api/bootstrap");
  const payload = await response.json();
  state.lastTree = payload.tree || [];
  renderTree(state.lastTree);
  setPaperStatus(payload.paperStatus || []);
}

async function saveActiveFile() {
  if (!state.activePath || !state.editable) {
    return;
  }
  const response = await fetch("/api/file", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: state.activePath, content: editorEl.value }),
  });
  const payload = await response.json();
  state.activeMtime = payload.mtime;
  state.dirty = false;
  updateEditorStatus(t("editor.saved"));
}

async function regenerateContext() {
  setHintText(logStatusEl, t("log.generatingContext"));
  const response = await fetch("/api/context/regenerate", { method: "POST" });
  const payload = await response.json();
  state.lastTree = payload.tree || [];
  renderTree(state.lastTree);
  setHintText(logStatusEl, t("log.contextUpdated"));
  if (state.activePath === payload.snapshotPath) {
    await openFile(payload.snapshotPath);
  }
}

async function compilePaper() {
  if (state.dirty && state.editable) {
    await saveActiveFile();
  }
  setHintText(logStatusEl, t("log.compiling"));
  buildLogEl.textContent = t("log.runningLatex");
  const response = await fetch("/api/compile", { method: "POST" });
  const payload = await response.json();
  buildLogEl.textContent = payload.log_text || payload.logText || t("log.noOutput");
  setHintText(logStatusEl, payload.success ? t("log.buildSucceeded") : t("log.buildFailed"));
  setPaperStatus(payload.paperStatus || []);
  state.lastTree = payload.tree || [];
  renderTree(state.lastTree);
  refreshPreview();
}

function refreshPreview(force = false) {
  pdfFrameEl.src = `/pdf/preview?ts=${Date.now()}`;
  setHintText(previewStatusEl, force ? t("preview.refreshed") : t("preview.synced"));
}

async function pollState() {
  const query = state.activePath ? `?path=${encodeURIComponent(state.activePath)}` : "";
  const response = await fetch(`/api/state${query}`);
  const payload = await response.json();

  if (payload.activePathMtime && state.activePath && payload.activePathMtime !== state.activeMtime) {
    if (!state.dirty) {
      await openFile(state.activePath);
      updateEditorStatus(t("editor.reloaded"));
    } else {
      updateEditorStatus(t("editor.externalChange"));
    }
  }

  if (payload.previewMtime && payload.previewMtime !== state.previewMtime) {
    state.previewMtime = payload.previewMtime;
    refreshPreview(true);
  }

  if (payload.logExcerpt) {
    buildLogEl.textContent = payload.logExcerpt;
  }
}

function updateEditorStatus(extraMessage = "") {
  if (!state.activePath) {
    setHintText(editorStatusEl, t("editor.noFileSelected"));
    return;
  }
  const parts = [];
  if (!state.editable) {
    parts.push(t("editor.readOnly"));
  }
  if (state.dirty) {
    parts.push(t("editor.unsavedChanges"));
  }
  if (extraMessage) {
    parts.push(extraMessage);
  }
  setHintText(editorStatusEl, parts.join(" | ") || t("editor.ready"));
}

function setPaperStatus(items) {
  const text = items.length > 0 ? items.join(" | ") : t("status.paperNotInitialized");
  paperStatusValueEl.textContent = text;
  paperStatusValueEl.dataset.hasValue = items.length > 0 ? "true" : "";
}

function setHintText(element, text) {
  element.textContent = text;
  element.dataset.hasValue = text ? "true" : "";
}

applyLanguage();

loadBootstrap().catch((error) => {
  buildLogEl.textContent = String(error);
  setHintText(logStatusEl, t("log.bootstrapFailed"));
});
