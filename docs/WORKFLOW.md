# Workflow Notes

Vibe Paper treats the experiment repository as the true source of evidence and the `paper/` directory as the writing workspace.

The default collaboration model is:

1. attach the agent to the whole experiment project
2. generate `paper/context/project_snapshot.md`
3. let the agent read the snapshot and then edit `paper/main.tex`
4. compile locally through the unified paper runtime
5. inspect the PDF, build log, and source changes in one place through the native desktop window

This separation matters:

- the experiment project remains the factual source of code, metrics, and artifacts
- the paper workspace remains the writable LaTeX output layer
- the desktop app remains the local Overleaf-like shell for preview and compilation

The human still owns claims and scientific judgment. Agents help with drafting, structure, consistency, figure placement, bibliography work, and iterative rewriting, but the paper should stay grounded in the real project files.
