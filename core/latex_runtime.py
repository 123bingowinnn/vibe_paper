from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


TEMP_OUTPUTS = [
    "main.aux",
    "main.bbl",
    "main.blg",
    "main.log",
    "main.out",
    "main.pdf",
    "main.synctex.gz",
    "main.toc",
]


@dataclass
class CompileResult:
    success: bool
    return_code: int
    message: str
    log_text: str
    preview_exists: bool
    formal_exists: bool

    def to_dict(self) -> dict:
        return asdict(self)


def compile_project_paper(project_root: Path) -> CompileResult:
    project_root = project_root.resolve()
    paper_dir = project_root / "paper"
    main_tex = paper_dir / "main.tex"
    if not main_tex.exists():
        return CompileResult(
            success=False,
            return_code=1,
            message="paper/main.tex was not found.",
            log_text="paper/main.tex was not found.\n",
            preview_exists=False,
            formal_exists=False,
        )

    build_dir = paper_dir / "build"
    build_tmp_dir = paper_dir / "build_tmp"
    build_dir.mkdir(parents=True, exist_ok=True)
    build_tmp_dir.mkdir(parents=True, exist_ok=True)

    for name in TEMP_OUTPUTS:
        path = build_tmp_dir / name
        if path.exists():
            path.unlink()

    pdflatex = resolve_tex_tool("pdflatex")
    bibtex = resolve_tex_tool("bibtex")
    command_logs: list[str] = []

    first = run_command(
        [str(pdflatex), "-interaction=nonstopmode", "-synctex=0", "-file-line-error", "-output-directory=build_tmp", "main.tex"],
        paper_dir,
    )
    command_logs.append(first)
    if not (build_tmp_dir / "main.pdf").exists():
        persist_log_only(build_tmp_dir, build_dir)
        return finalize_failure(build_dir, command_logs, "The first pdflatex pass failed.")

    if requires_bibliography(main_tex):
        bib = run_command([str(bibtex), "build_tmp/main"], paper_dir)
        command_logs.append(bib)
        if "error" in bib.lower() and not (build_tmp_dir / "main.bbl").exists():
            persist_log_only(build_tmp_dir, build_dir)
            return finalize_failure(build_dir, command_logs, "BibTeX failed.")

    second = run_command(
        [str(pdflatex), "-interaction=nonstopmode", "-synctex=0", "-file-line-error", "-output-directory=build_tmp", "main.tex"],
        paper_dir,
    )
    third = run_command(
        [str(pdflatex), "-interaction=nonstopmode", "-synctex=0", "-file-line-error", "-output-directory=build_tmp", "main.tex"],
        paper_dir,
    )
    command_logs.extend([second, third])

    final_pdf = build_tmp_dir / "main.pdf"
    if not final_pdf.exists():
        persist_log_only(build_tmp_dir, build_dir)
        return finalize_failure(build_dir, command_logs, "The final PDF was not generated.")

    copy_success_outputs(build_tmp_dir, build_dir)
    log_text = collect_combined_log(build_dir / "main.log", command_logs)
    return CompileResult(
        success=True,
        return_code=0,
        message="Paper compiled successfully.",
        log_text=log_text,
        preview_exists=(build_dir / "main_preview.pdf").exists(),
        formal_exists=(build_dir / "main.pdf").exists(),
    )


def resolve_tex_tool(name: str) -> Path:
    path_candidate = shutil.which(name)
    if path_candidate:
        return Path(path_candidate)

    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64" / f"{name}.exe",
        Path(os.environ.get("ProgramFiles", "")) / "MiKTeX" / "miktex" / "bin" / "x64" / f"{name}.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "MiKTeX" / "miktex" / "bin" / "x64" / f"{name}.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find {name}. Install MiKTeX or TeX Live and expose {name} on PATH.")


def requires_bibliography(main_tex: Path) -> bool:
    try:
        content = main_tex.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = main_tex.read_text(encoding="utf-8", errors="replace")
    return "\\cite{" in content or "\\nocite{" in content


def run_command(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    joined = " ".join(command)
    output = [f"$ {joined}", result.stdout.strip(), result.stderr.strip()]
    return "\n".join(part for part in output if part) + "\n"


def copy_success_outputs(build_tmp_dir: Path, build_dir: Path) -> None:
    mapping = [
        ("main.pdf", "main.pdf"),
        ("main.pdf", "main_preview.pdf"),
        ("main.log", "main.log"),
        ("main.aux", "main.aux"),
        ("main.bbl", "main.bbl"),
        ("main.blg", "main.blg"),
    ]
    for source_name, dest_name in mapping:
        source = build_tmp_dir / source_name
        if source.exists():
            shutil.copy2(source, build_dir / dest_name)


def persist_log_only(build_tmp_dir: Path, build_dir: Path) -> None:
    log_path = build_tmp_dir / "main.log"
    if log_path.exists():
        shutil.copy2(log_path, build_dir / "main.log")


def finalize_failure(build_dir: Path, command_logs: list[str], message: str) -> CompileResult:
    log_text = collect_combined_log(build_dir / "main.log", command_logs)
    return CompileResult(
        success=False,
        return_code=1,
        message=message,
        log_text=log_text,
        preview_exists=(build_dir / "main_preview.pdf").exists(),
        formal_exists=(build_dir / "main.pdf").exists(),
    )


def collect_combined_log(log_path: Path, command_logs: list[str]) -> str:
    parts = []
    if log_path.exists():
        try:
            parts.append(log_path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    parts.extend(command_logs)
    return "\n\n".join(part.strip() for part in parts if part).strip() + "\n"

