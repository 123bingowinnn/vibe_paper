# Troubleshooting

## The browser opens but there is no paper preview

Initialize the project first. `paper/` and `paper/context/project_snapshot.md` must exist before the web app can show a meaningful paper workflow.

## The PDF is damaged or blank

Open `paper/build/main_preview.pdf` instead of `paper/build/main.pdf`. The preview copy exists to avoid half-written PDF files during compilation.

## `pdflatex` or `bibtex` is not recognized

Install MiKTeX or TeX Live and confirm that `pdflatex` and `bibtex` work in a fresh terminal window.

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check-latex-env.ps1
```

## Flask is missing

Install the Python dependency:

```powershell
pip install -r requirements.txt
```

## The paper compiles in the terminal but not in the app

Make sure the app is pointing at the experiment project root that contains `paper/`, not at the repository root of Vibe Paper itself.

## The agent ignores project results

Regenerate `paper/context/project_snapshot.md` from the UI or by running the scan command. The snapshot is the shared evidence index that the agent is expected to read first.
