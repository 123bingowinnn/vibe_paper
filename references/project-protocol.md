# Project Protocol

Vibe Paper assumes that the experiment repository is the factual source of truth. The project root is readable context. The `paper/` directory is the writable paper workspace.

The default writable locations are:

- `paper/main.tex`
- `paper/references/`
- `paper/figures/`
- `paper/scripts/`
- `paper/build/`
- `paper/context/project_snapshot.md`

Agents should read `paper/context/project_snapshot.md` before rewriting prose. That snapshot is the shared entry point for project overview, file structure, metrics hints, artifact paths, and paper status.

Agents should preserve claims and numbers from real files. They should prefer structured metrics in JSON, CSV, logs, or evaluation outputs over prose summaries. They should not invent dataset sizes, baselines, or measurements.

When local compilation is needed, use the repository build flow rather than editor-specific commands. The preview-safe output is `paper/build/main_preview.pdf`.
