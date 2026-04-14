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

## Trigger patterns

Use this skill when the user asks to do any of the following inside a real experiment repository:

- turn the repository into a local paper workspace
- create or refresh `paper/context/project_snapshot.md`
- write or revise `paper/main.tex`
- compile the paper locally
- open or refresh the native popup PDF preview
- use the repository itself as the paper-writing context for Codex, Cursor, or Claude Code

## Default command flow

When the user wants the full local paper loop, follow this sequence:

1. Run `scripts/check-env.ps1` if the environment is unknown.
2. Run `scripts/init-workspace.ps1` if `paper/` does not exist yet.
3. Read `paper/context/project_snapshot.md`.
4. Edit `paper/main.tex` and related paper files.
5. Run `scripts/open-preview.ps1` if the user wants the native popup preview.

Inside the popup preview, the main visible action is `Update`, which compiles the paper and refreshes the preview in one step.

## Minimal examples

For a fresh repository:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\init-workspace.ps1 -ProjectRoot <PROJECT_ROOT> -Title "<TITLE>" -Author "<AUTHOR>" -Affiliation "<AFFILIATION>" -Email "<EMAIL>"
powershell -ExecutionPolicy Bypass -File .\scripts\open-preview.ps1 -ProjectRoot <PROJECT_ROOT>
```

For an existing paper workspace:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\open-preview.ps1 -ProjectRoot <PROJECT_ROOT>
```

## Agent usage contract

Treat the whole project root as readable evidence. Do not limit attention to `paper/`.

Read this file first when it exists:

```text
paper/context/project_snapshot.md
```

Then edit:

```text
paper/main.tex
```

Preserve claims, numbers, dataset descriptions, and comparisons from real files. Do not invent missing metrics or sources.

## What to read next

Read `references/project-protocol.md` when you need the project-root and `paper/` workspace contract. Read `references/popup-preview.md` when you need the native preview flow, script entrypoints, or desktop behavior. Read `references/skill-invocation.md` when you need exact invocation examples for Codex, Cursor, or Claude Code.
