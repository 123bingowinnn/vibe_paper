# Troubleshooting

## The desktop window opens but there is no paper preview

Initialize the project first. `paper/` and `paper/context/project_snapshot.md` must exist before Vibe Paper can show a meaningful paper workflow.

## The PDF is damaged or blank

Open `paper/build/main_preview.pdf` instead of `paper/build/main.pdf`. The preview copy exists to avoid half-written PDF files during compilation.

## `pdflatex` or `bibtex` is not recognized

Install MiKTeX or TeX Live and confirm that `pdflatex` and `bibtex` work in a fresh terminal window.

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
```

## `pdftoppm` is missing

Vibe Paper uses a local PDF rasterizer to turn the preview PDF into pages that the desktop app can display. Install MiKTeX or make sure its `pdftoppm.exe` is visible on `PATH`.

## PyQt5 is missing

Install the Python dependency:

```powershell
pip install -r requirements.txt
```

## The paper compiles in the terminal but not in the desktop app

Make sure the app is pointing at the experiment project root that contains `paper/`, not at the repository root of Vibe Paper itself.

## The agent ignores project results

Regenerate `paper/context/project_snapshot.md` with `Ctrl+Shift+G` inside the popup preview, or rerun `scripts\init-workspace.ps1`. The snapshot is the shared evidence index that the agent is expected to read first.
