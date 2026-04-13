# Vibe Paper

A local-first, agent-native paper workspace for writing LaTeX papers directly inside real experiment projects.

Vibe Paper is built for a workflow where the experiment repository remains the root workspace, agents such as Codex, Cursor, and Claude Code read the real code, configs, logs, and result files, the paper lives in `paper/` inside the same project, compilation happens locally with LaTeX, and a lightweight web app provides editing, build logs, and PDF preview without depending on VS Code preview.

## Core Idea

Instead of asking an agent to draft a paper from detached chat history, Vibe Paper attaches the agent to the whole experiment folder. The agent reads real project evidence, writes real LaTeX files, and works against a local compile loop.

That makes the workflow much closer to a local, single-user version of Overleaf, while preserving full control of the files and the build chain.

## What This Repository Includes

- a project-aware `paper/` initializer
- a reusable IEEE-style paper template
- a stable local LaTeX build backend
- a local web app for editing, compiling, logging, and previewing PDFs
- automatic generation of `paper/context/project_snapshot.md`
- adapters for Codex, Cursor, and Claude Code
- example projects for smoke testing the workflow

## Repository Layout

```text
vibe-paper/
|-- adapters/
|-- app/
|-- core/
|-- docs/
|-- examples/
|-- templates/
`-- tools/
```

## Quick Start

### 1. Check the environment

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check-latex-env.ps1
```

This checks for:

- `python`
- `Flask`
- `pdflatex`
- `bibtex`

### 2. Initialize `paper/` inside an experiment project

Use the included example experiment:

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

```text
examples\toy-experiment\paper\
```

and also generates:

```text
examples\toy-experiment\paper\context\project_snapshot.md
```

### 3. Start the local web app

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start-vibe-paper.ps1 `
  -ProjectRoot .\examples\toy-experiment
```

The browser UI provides:

- a project file tree
- a built-in text editor
- one-click context generation
- one-click compilation
- build logs
- PDF preview through `main_preview.pdf`

### 4. Point your agent at the same project root

Attach Codex, Cursor, or Claude Code to:

```text
examples\toy-experiment
```

The agent should read:

```text
paper/context/project_snapshot.md
```

first, and then draft or edit `paper/main.tex`.

## Why `project_snapshot.md` Exists

Different agents can behave inconsistently if they each rediscover the project from scratch. Vibe Paper therefore generates a shared context file under `paper/context/` that summarizes project overview, top-level structure, key code files, key config files, dataset and experiment hints, exported metrics and artifact paths, and current paper workspace status.

This gives all agents a common paper-writing entry point.

## Why `main_preview.pdf` Exists

Local editor preview can occasionally open a half-written PDF during compilation on Windows. Vibe Paper therefore keeps:

- `main.pdf` as the formal output
- `main_preview.pdf` as the safer preview copy

The web app always prefers the preview copy.

## Adapters

See:

- `adapters/codex/`
- `adapters/cursor/`
- `adapters/claude-code/`

These adapters do not replace the core runtime. They only tell each agent how to behave inside the same project protocol.

## Example Projects

- `examples/ieee-sample/`: a minimal standalone paper workspace
- `examples/toy-experiment/`: a toy experiment repo intended for project-root ingestion

## Documentation

- [Quickstart](./docs/QUICKSTART.md)
- [Beginner Guide](./docs/BEGINNER_GUIDE.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [Workflow Notes](./docs/WORKFLOW.md)
- [Publish to GitHub](./docs/PUBLISH_TO_GITHUB.md)

## License

MIT
