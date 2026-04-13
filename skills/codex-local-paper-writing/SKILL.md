# Codex Local Paper Writing

Use this skill when Codex is attached to an experiment project that uses the Vibe Paper workflow.

## Purpose

Help Codex behave like a careful paper-writing teammate inside a real project root:

- read the whole project, not only `paper/`
- use `paper/context/project_snapshot.md` as the first paper-writing context file
- edit real LaTeX files instead of pasting large fragments manually
- preserve claims and numeric results from the project files
- compile locally after non-trivial edits

## Expected Layout

```text
project-root/
├── code, configs, logs, and results
└── paper/
    ├── context/
    ├── figures/
    ├── references/
    ├── build/
    ├── build_tmp/
    ├── build_paper.bat
    └── main.tex
```

## Workflow

1. Read `paper/context/project_snapshot.md` first.
2. Read `paper/main.tex` before rewriting.
3. Preserve LaTeX commands such as `\cite{}`, `\ref{}`, equations, and labels.
4. Do not invent citations or metrics.
5. Keep terminology consistent across sections.
6. After substantial edits, run the paper build flow.
7. If preview is unstable, open `paper/build/main_preview.pdf`.

## Editing Principles

- Prefer precise academic English over ornate wording.
- Do not change claims or numbers unless the source files justify the change.
- Treat code, configs, exported metrics, and logs as the factual evidence base.
- Keep bibliography files explicit and versioned.
