# Quickstart

## Recommended first run

1. Run `scripts\check-env.ps1`.
2. Initialize `paper/` inside `examples\toy-experiment`.
3. Launch the native preview popup with `scripts\open-preview.ps1`.
4. Open the project root in your agent and let it work against the same files.

For Codex, you can explicitly invoke the repository skill with prompts such as:

- `Use $vibe-paper to initialize the paper workspace in this repository.`
- `Use $vibe-paper to open the popup preview for this project.`

## Initialize a project-aware paper workspace

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-workspace.ps1 `
  -ProjectRoot .\examples\toy-experiment `
  -Title "A Toy Detector Paper" `
  -Author "Sample Author" `
  -Affiliation "Open Research Workflow Lab" `
  -Email "sample@example.com" `
  -Force
```

This creates:

- `paper/main.tex`
- `paper/references/`
- `paper/figures/`
- `paper/build/`
- `paper/context/project_snapshot.md`

## Launch the native preview popup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\open-preview.ps1 `
  -ProjectRoot .\examples\toy-experiment
```

The native popup window gives you:

- a preview-first PDF window
- a minimal HUD for update, open-PDF, and file access
- one optional file browser button
- hidden advanced panels for files, source, and logs via shortcuts
- PDF preview based on `paper/build/main_preview.pdf`

## Agent workflow

Point your agent at the experiment project root, not only at `paper/`.

The first file the agent should read is:

```text
paper/context/project_snapshot.md
```

Then it should edit:

```text
paper/main.tex
```

For Codex, the repository itself is the skill. For other agents, follow the notes in `adapters/`.
