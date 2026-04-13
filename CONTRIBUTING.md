# Contributing

Thank you for improving Vibe Paper.

## Ground rules

Keep the project local-first. The core promise of the repository is that the paper workspace lives inside a real experiment project and compiles through the local LaTeX runtime.

## When making changes

- preserve the `paper/`-inside-project model
- keep the compile backend shared by the CLI and the web app
- avoid editor-specific assumptions
- prefer evidence-preserving workflows over convenience shortcuts

## Before opening a pull request

- run the environment check
- initialize the example project if needed
- compile the example project successfully
- confirm that `paper/context/project_snapshot.md` still regenerates correctly
