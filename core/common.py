from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "build",
    "build_tmp",
    ".pytest_cache",
    ".mypy_cache",
}

METADATA_ONLY_DIRS = {
    "data",
    "dataset",
    "datasets",
    "weights",
    "checkpoints",
    "ckpt",
    "wandb",
    "artifacts",
}

TEXT_EDITABLE_EXTENSIONS = {
    ".bib",
    ".cls",
    ".csv",
    ".json",
    ".log",
    ".md",
    ".py",
    ".ps1",
    ".sh",
    ".sty",
    ".tex",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

CODE_EXTENSIONS = {".py", ".ipynb", ".sh", ".ps1", ".js", ".ts"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}
RESULT_EXTENSIONS = {".json", ".csv", ".txt", ".log"} | IMAGE_EXTENSIONS

MAX_TEXT_BYTES = 200_000
LARGE_FILE_BYTES = 5 * 1024 * 1024
MAX_TRACKED_FILES = 1500


def normalize_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def resolve_within_root(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    root_resolved = root.resolve()
    if os.name == "nt":
        candidate_text = str(candidate).lower()
        root_text = str(root_resolved).lower()
        if not candidate_text.startswith(root_text):
            raise ValueError(f"Path escapes project root: {relative_path}")
    elif root_resolved not in candidate.parents and candidate != root_resolved:
        raise ValueError(f"Path escapes project root: {relative_path}")
    return candidate


def is_text_editable(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EDITABLE_EXTENSIONS


def read_small_text(path: Path, default: str = "") -> str:
    if not path.exists() or path.stat().st_size > MAX_TEXT_BYTES:
        return default
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return default


def iter_project_files(root: Path) -> Iterable[Path]:
    count = 0
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in sorted(dirnames)
            if name.lower() not in IGNORE_DIRS
        ]
        current_path = Path(current_root)
        for filename in sorted(filenames):
            yield current_path / filename
            count += 1
            if count >= MAX_TRACKED_FILES:
                return


def build_tree(root: Path, current: Path | None = None) -> list[dict]:
    current = current or root
    nodes: list[dict] = []
    entries = sorted(
        current.iterdir(),
        key=lambda item: (
            0 if item.is_dir() else 1,
            priority_name(item.name),
            item.name.lower(),
        ),
    )
    for entry in entries:
        if entry.name.lower() in IGNORE_DIRS:
            continue
        rel_path = normalize_relative(entry, root)
        node = {
            "name": entry.name,
            "path": rel_path,
            "type": "dir" if entry.is_dir() else "file",
            "highlight": highlight_name(entry.name),
        }
        if entry.is_dir():
            metadata_only = entry.name.lower() in METADATA_ONLY_DIRS
            node["metadataOnly"] = metadata_only
            node["children"] = [] if metadata_only else build_tree(root, entry)
        nodes.append(node)
    return nodes


def highlight_name(name: str) -> str | None:
    lowered = name.lower()
    if lowered == "paper":
        return "paper"
    if lowered in {"results", "outputs", "reports"}:
        return "results"
    if lowered in {"scripts", "src"}:
        return "code"
    if lowered in {"configs", "config"}:
        return "config"
    if lowered == "logs":
        return "logs"
    return None


def priority_name(name: str) -> int:
    lowered = name.lower()
    order = {
        "paper": 0,
        "results": 1,
        "src": 2,
        "scripts": 3,
        "configs": 4,
        "logs": 5,
        "readme.md": 6,
    }
    return order.get(lowered, 20)
