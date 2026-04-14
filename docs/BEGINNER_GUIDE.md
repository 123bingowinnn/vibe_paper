# Beginner Guide

## Who this is for

This guide is for users who already have an experiment project on disk and want to turn it into a paper-writing workspace without learning the full repository structure first.

## What Vibe Paper does

Vibe Paper does not replace LaTeX. It packages a local LaTeX workflow as a skill and runtime so that:

- your experiment project remains the real source of evidence
- your paper lives in `paper/` inside that same project
- an agent can read the code, configs, logs, and results before it writes
- a native popup preview gives you PDF preview, compile logs, and optional editing in one place

## The shortest path to a working demo

### 1. Check the environment

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
```

If `pdflatex`, `bibtex`, `pdftoppm`, or `PyQt5` is missing, fix that first.

### 2. Initialize the example project

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-workspace.ps1 `
  -ProjectRoot .\examples\toy-experiment `
  -Title "A Toy Detector Paper" `
  -Author "Sample Author" `
  -Affiliation "Open Research Workflow Lab" `
  -Email "sample@example.com" `
  -Force
```

This creates `paper/` inside the example experiment and generates `paper/context/project_snapshot.md`.

### 3. Launch the popup preview

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\open-preview.ps1 `
  -ProjectRoot .\examples\toy-experiment
```

Then a native preview window opens on your desktop.

## What you will see

The popup preview has four main areas:

- the center previews `paper/build/main_preview.pdf`
- the left file tree can be shown or hidden
- the source editor can be shown or hidden
- the bottom log panel can be shown or hidden

## What the top buttons do

- `Context`: rescans the experiment project and rewrites `paper/context/project_snapshot.md`
- `Save`: saves the file that is currently open in the editor
- `Compile`: runs the local LaTeX build backend
- `Refresh`: reloads the preview PDF
- `PDF`: opens `paper/build/main.pdf`
- `Files`, `Source`, and `Log`: toggle the optional side panels
- the language toggle switches the UI between English and Chinese

## How to use it with an agent

Open the same experiment project root in Codex, Cursor, or Claude Code. Do not point the agent only at `paper/`.

For Codex, this repository itself is the `vibe-paper` skill.

Tell the agent to read:

```text
paper/context/project_snapshot.md
```

first, then edit:

```text
paper/main.tex
```

The point of this workflow is that the agent can see the real project evidence before it writes the paper.

## Using your own experiment project

If your project is stored at `D:\MyProject`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-workspace.ps1 `
  -ProjectRoot D:\MyProject `
  -Title "Your Paper Title" `
  -Author "Your Name" `
  -Affiliation "Your Lab" `
  -Email "you@example.com"
```

Then start the desktop app:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\open-preview.ps1 `
  -ProjectRoot D:\MyProject
```

## If something goes wrong

If the PDF is blank or damaged, open `paper/build/main_preview.pdf` instead of `paper/build/main.pdf`.

If the app starts but nothing useful appears, regenerate the context file.

If LaTeX is missing, install MiKTeX or TeX Live and rerun the environment check.
