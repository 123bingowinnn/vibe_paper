from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from .common import TEMPLATES_DIR
from .project_context import write_project_snapshot


def init_project_paper(
    project_root: Path,
    title: str | None = None,
    author: str = "Author Name",
    affiliation: str = "School / Department",
    email: str = "author@example.com",
    force: bool = False,
) -> Path:
    project_root = project_root.resolve()
    if not project_root.exists():
        raise FileNotFoundError(f"Project root does not exist: {project_root}")

    template_dir = TEMPLATES_DIR / "ieee-paper"
    paper_dir = project_root / "paper"

    if paper_dir.exists():
        if not force:
            raise FileExistsError("paper/ already exists. Use --force to overwrite it.")
        shutil.rmtree(paper_dir)

    shutil.copytree(template_dir, paper_dir)
    final_title = title or default_title(project_root.name)
    replace_template_metadata(paper_dir / "main.tex", final_title, author, affiliation, email)
    stamp_runtime_paths(paper_dir)
    generate_template_figure(paper_dir)
    write_project_snapshot(project_root)
    return paper_dir


def replace_template_metadata(
    main_tex: Path,
    title: str,
    author: str,
    affiliation: str,
    email: str,
) -> None:
    content = main_tex.read_text(encoding="utf-8")
    content = content.replace("__PAPER_TITLE__", title)
    content = content.replace("__AUTHOR_NAME__", author)
    content = content.replace("__AFFILIATION__", affiliation)
    content = content.replace("__EMAIL__", email)
    main_tex.write_text(content, encoding="utf-8")


def generate_template_figure(paper_dir: Path) -> None:
    figure_script = paper_dir / "scripts" / "generate_demo_figure.py"
    if not figure_script.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(figure_script)],
            cwd=paper_dir,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return


def stamp_runtime_paths(paper_dir: Path) -> None:
    vibe_paper_home = str(TEMPLATES_DIR.parent)
    for relative_path in ("build_paper.bat", "scripts/run_vibe_build.py"):
        file_path = paper_dir / relative_path
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        content = content.replace("__VIBE_PAPER_HOME__", vibe_paper_home)
        file_path.write_text(content, encoding="utf-8")


def default_title(project_name: str) -> str:
    words = project_name.replace("_", " ").replace("-", " ").strip()
    if not words:
        return "Project Paper Title"
    return " ".join(part.capitalize() for part in words.split())
