# Quickstart

## Recommended first run

1. Run `tools\check-latex-env.ps1`.
2. Initialize `paper/` inside `examples\toy-experiment`.
3. Start the web app with `tools\start-vibe-paper.ps1`.
4. Open the project root in your agent and let it work against the same files.

## Initialize a project-aware paper workspace

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\init-vibe-paper.ps1 `
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

## Start the local web app

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start-vibe-paper.ps1 `
  -ProjectRoot .\examples\toy-experiment
```

The browser UI gives you:

- a file tree rooted at the whole experiment project
- a text editor for LaTeX and related source files
- compile and context-generation buttons
- build logs
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
