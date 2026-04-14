---
name: vibe-paper
description: Local-first LaTeX paper workspace skill for research repositories. Use when Codex is attached to a real experiment project and needs to initialize or maintain a `paper/` workspace, generate `paper/context/project_snapshot.md`, edit real LaTeX and bibliography files, compile locally, or launch the native popup PDF preview against project evidence.
---

# Vibe Paper

Use this skill when the project root contains real code, configs, logs, metrics, figures, and a local `paper/` directory or is about to create one.

## Core workflow

Read `paper/context/project_snapshot.md` first when it exists. Treat the whole project root as readable evidence and `paper/` as the writable paper layer. Keep claims, numbers, dataset descriptions, and baselines grounded in real files.

If the workspace does not exist yet, run `scripts/init-workspace.ps1`. If the user wants a native popup preview, run `scripts/open-preview.ps1`. If the environment needs checking first, run `scripts/check-env.ps1`.

When editing the paper, change real `.tex`, `.bib`, and figure files instead of pasting detached fragments. When compilation is needed, use the repository build flow and inspect `paper/build/main_preview.pdf` or the popup preview rather than relying on editor-specific preview features.

## What to read next

Read `references/project-protocol.md` when you need the project-root and `paper/` workspace contract. Read `references/popup-preview.md` when you need the native preview flow, script entrypoints, or desktop behavior.
