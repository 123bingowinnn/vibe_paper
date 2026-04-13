---
name: vibe-paper-codex
description: Local-first paper-writing adapter for Codex. Use when Codex is attached to an experiment project that contains a `paper/` workspace created by Vibe Paper, and the goal is to draft, edit, compile, or inspect a LaTeX paper by reading the whole project root rather than only the paper folder.
---

# Vibe Paper for Codex

Use this adapter when working on a research project that contains source code, configs, logs, result files, and a local `paper/` directory.

## Default workflow

1. Read `paper/context/project_snapshot.md` first.
2. Read `paper/main.tex` before rewriting paper text.
3. Use the whole project root as context, but preserve claims and numbers from real files.
4. Edit real LaTeX and bibliography files rather than pasting detached fragments.
5. When compilation is needed, use the Vibe Paper build flow instead of editor-specific build actions.

## Important rules

- Treat the entire project root as readable context.
- Treat `paper/` as the writable paper workspace.
- Do not invent missing metrics, dataset sizes, or baselines.
- If the project has structured metrics in JSON or CSV, prefer those over prose descriptions.
- If preview is needed, use `paper/build/main_preview.pdf`.

