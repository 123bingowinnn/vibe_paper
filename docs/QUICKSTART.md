# Quickstart

## Recommended first run

1. Run `scripts\check-env.ps1`.
2. Initialize `paper/` inside `examples\toy-experiment`.
3. Launch the native preview popup with `scripts\open-preview.ps1`.
4. Open the project root in your agent and let it work against the same files.

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
- a collapsible file tree rooted at the whole experiment project
- an optional text editor for LaTeX and related source files
- compile and context-generation buttons
- a collapsible build log
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
