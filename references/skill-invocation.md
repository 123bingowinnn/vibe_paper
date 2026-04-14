# Skill Invocation

This file is the exact invocation reference for using Vibe Paper as a skill-driven workflow.

## What the skill is for

Vibe Paper is not a cloud editor. It is a local paper workspace protocol for real experiment repositories.

Use it when:

- the repository already contains code, configs, logs, metrics, figures, or result files
- the agent should write the paper from those real files
- the user wants a local popup preview instead of editor-specific PDF preview
- the paper should live in `paper/` inside the same project

## What the skill should do

The skill should help the agent do four things:

1. initialize `paper/` when needed
2. regenerate `paper/context/project_snapshot.md`
3. edit real LaTeX paper files
4. open the native popup preview and work against local LaTeX compilation

## Exact script entrypoints

Check environment:

```powershell
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\scripts\check-env.ps1
```

Initialize a paper workspace:

```powershell
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\scripts\init-workspace.ps1 -ProjectRoot <PROJECT_ROOT> -Title "<TITLE>" -Author "<AUTHOR>" -Affiliation "<AFFILIATION>" -Email "<EMAIL>"
```

Open the native popup preview:

```powershell
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\scripts\open-preview.ps1 -ProjectRoot <PROJECT_ROOT> -Lang zh
```

## Exact Codex usage

When Codex is attached to the experiment repository, the user can say:

- `Use $vibe-paper to turn this repository into a paper workspace.`
- `Use $vibe-paper to open the popup preview for this project.`
- `Use $vibe-paper to update the paper from the project snapshot and compile it locally.`

The expected Codex behavior is:

1. check whether `paper/` exists
2. initialize it if missing
3. read `paper/context/project_snapshot.md`
4. edit `paper/main.tex`
5. use the local compile and preview loop

## Exact Cursor usage

Attach Cursor to the experiment repository root, not only to `paper/`.

Then use a rule or prompt such as:

```text
Use the Vibe Paper workflow for this repository. Read paper/context/project_snapshot.md first, edit paper/main.tex, and use the local popup preview workflow instead of editor-native PDF preview.
```

## Exact Claude Code usage

Attach Claude Code to the experiment repository root and use a prompt such as:

```text
Use the vibe-paper skill protocol for this repository. Treat the whole project as evidence, read paper/context/project_snapshot.md first, write the paper under paper/, and use the local popup preview workflow.
```

## Popup preview behavior

The popup preview is intentionally minimal.

Visible HUD actions:

- `Update`: compile and refresh preview
- `PDF`: open `paper/build/main.pdf`
- `Files`: open or hide the optional file browser
- language toggle

Hidden advanced controls:

- `Ctrl+2`: source editor
- `Ctrl+3`: build log
- `Ctrl+S`: save current source file
- `Ctrl+Shift+G`: regenerate `paper/context/project_snapshot.md`

## What not to do

- Do not invent metrics that do not exist in the repository.
- Do not treat chat history as the source of truth when files exist.
- Do not rely on VS Code preview as the primary preview path.
- Do not write the paper outside `paper/` unless the repository is explicitly structured differently.
