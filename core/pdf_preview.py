from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class PdfPreviewError(RuntimeError):
    """Raised when the local PDF preview images cannot be generated."""


def resolve_pdf_renderer() -> tuple[Path, str]:
    direct_candidate = shutil.which("pdftoppm")
    if direct_candidate:
        return Path(direct_candidate), "pdftoppm"

    cairo_candidate = shutil.which("pdftocairo")
    if cairo_candidate:
        return Path(cairo_candidate), "pdftocairo"

    miktex_bin = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64",
        Path(os.environ.get("ProgramFiles", "")) / "MiKTeX" / "miktex" / "bin" / "x64",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "MiKTeX" / "miktex" / "bin" / "x64",
    ]
    name_candidates = [
        ("pdftoppm.exe", "pdftoppm"),
        ("miktex-pdftoppm.exe", "pdftoppm"),
        ("pdftocairo.exe", "pdftocairo"),
        ("miktex-pdftocairo.exe", "pdftocairo"),
    ]
    for base_dir in miktex_bin:
        for filename, renderer_type in name_candidates:
            candidate = base_dir / filename
            if candidate.exists():
                return candidate, renderer_type

    raise PdfPreviewError(
        "Could not find a local PDF rasterizer. Install MiKTeX or expose pdftoppm on PATH."
    )


def render_pdf_preview_pages(pdf_path: Path, output_dir: Path, dpi: int = 144) -> list[Path]:
    pdf_path = pdf_path.resolve()
    output_dir = output_dir.resolve()
    if not pdf_path.exists():
        raise PdfPreviewError(f"Preview PDF was not found: {pdf_path}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    renderer_path, renderer_type = resolve_pdf_renderer()
    prefix = output_dir / "page"
    command = [str(renderer_path), "-png", "-r", str(dpi), str(pdf_path), str(prefix)]
    if renderer_type == "pdftocairo":
        command = [str(renderer_path), "-png", "-r", str(dpi), str(pdf_path), str(prefix)]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        details = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
        raise PdfPreviewError(details or "The PDF preview renderer returned a non-zero exit code.")

    pages = sorted(output_dir.glob("page-*.png"), key=_page_sort_key)
    if not pages:
        raise PdfPreviewError("The PDF preview renderer did not generate any page images.")
    return pages


def _page_sort_key(path: Path) -> int:
    stem = path.stem
    try:
        return int(stem.split("-")[-1])
    except ValueError:
        return 10**9
