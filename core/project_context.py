from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from .common import (
    CODE_EXTENSIONS,
    CONFIG_EXTENSIONS,
    IMAGE_EXTENSIONS,
    LARGE_FILE_BYTES,
    RESULT_EXTENSIONS,
    iter_project_files,
    normalize_relative,
    read_small_text,
)


TEXT_HINT_KEYWORDS = ("dataset", "data", "train", "valid", "test", "split", "metric", "result")
TOP_README_NAMES = ("README.md", "readme.md", "README.txt")


def write_project_snapshot(project_root: Path) -> Path:
    snapshot = build_project_snapshot(project_root)
    context_dir = project_root / "paper" / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = context_dir / "project_snapshot.md"
    snapshot_path.write_text(snapshot, encoding="utf-8")
    return snapshot_path


def build_project_snapshot(project_root: Path) -> str:
    project_root = project_root.resolve()
    scan = scan_project(project_root)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    top_level_lines = [f"- `{item}`" for item in scan["top_level"]] or ["- No top-level entries were summarized."]
    code_lines = [f"- `{item}`" for item in scan["code_files"]] or ["- No key code files were detected."]
    config_lines = [f"- `{item}`" for item in scan["config_files"]] or ["- No key config files were detected."]
    dataset_lines = [f"- {item}" for item in scan["dataset_hints"]] or ["- No explicit dataset hints were extracted."]
    metric_lines = [f"- {item}" for item in scan["metrics"]] or ["- No structured metric summaries were extracted."]
    artifact_lines = [f"- `{item}`" for item in scan["artifacts"]] or ["- No figure or artifact paths were indexed."]
    large_file_lines = [f"- {item}" for item in scan["large_files"]] or ["- No large artifacts were detected."]
    paper_status_lines = [f"- {item}" for item in scan["paper_status"]] or ["- `paper/` does not exist yet. Initialize the paper workspace before writing."]

    sections = [
        f"# Project Snapshot: {project_root.name}",
        "",
        f"Generated at: {generated_at}",
        "",
        "## What This Snapshot Is For",
        "",
        "This file is the default paper-writing context for agents working on the project. "
        "Read this file first, then read `paper/main.tex`, and only after that open additional source files or result files as needed.",
        "",
        "## Project Overview",
        "",
        scan["overview"] or "No top-level README summary was found.",
        "",
        "## Top-Level Structure",
        "",
        *top_level_lines,
        "",
        "## Key Code Entry Points",
        "",
        *code_lines,
        "",
        "## Key Config Files",
        "",
        *config_lines,
        "",
        "## Dataset and Experiment Hints",
        "",
        *dataset_lines,
        "",
        "## Result Files and Extracted Metrics",
        "",
        *metric_lines,
        "",
        "## Figures and Artifact Paths",
        "",
        *artifact_lines,
        "",
        "## Large Files Recorded as Metadata Only",
        "",
        *large_file_lines,
        "",
        "## Paper Workspace Status",
        "",
        *paper_status_lines,
        "",
        "## Agent Workflow Reminder",
        "",
        "- Treat the whole project root as the working scope.",
        "- Use `paper/` as the location for LaTeX, references, scripts, and build outputs.",
        "- Preserve claims and numeric results from the project files. Do not invent missing metrics.",
        "- If paper compilation is required, use the unified paper build command rather than editor-specific build actions.",
    ]
    return "\n".join(sections).strip() + "\n"


def scan_project(project_root: Path) -> dict:
    overview = extract_overview(project_root)
    top_level = summarize_top_level(project_root)
    code_files: list[str] = []
    config_files: list[str] = []
    dataset_hints: list[str] = []
    metrics: list[str] = []
    artifacts: list[str] = []
    large_files: list[str] = []

    for path in iter_project_files(project_root):
        rel = normalize_relative(path, project_root)
        suffix = path.suffix.lower()

        if rel.startswith("paper/"):
            continue

        if path.stat().st_size >= LARGE_FILE_BYTES:
            large_files.append(format_large_file(rel, path.stat().st_size))
            continue

        if suffix in CODE_EXTENSIONS and len(code_files) < 12:
            code_files.append(rel)

        if (
            suffix in CONFIG_EXTENSIONS
            and not any(token in rel.lower() for token in ("logs/", "results/", "outputs/"))
            and len(config_files) < 12
        ):
            config_files.append(rel)

        if suffix in IMAGE_EXTENSIONS and any(part.lower() in {"results", "figures", "outputs"} for part in path.parts):
            if len(artifacts) < 12:
                artifacts.append(rel)

        if suffix in RESULT_EXTENSIONS:
            metric_summary = summarize_result_file(path, project_root)
            if metric_summary and len(metrics) < 16:
                metrics.append(metric_summary)

        if suffix in {".md", ".txt", ".yaml", ".yml", ".json", ".csv"} and len(dataset_hints) < 12:
            dataset_hints.extend(extract_dataset_hints(path, project_root, limit=12 - len(dataset_hints)))

    paper_status = summarize_paper_status(project_root)
    return {
        "overview": overview,
        "top_level": top_level,
        "code_files": dedupe(code_files),
        "config_files": dedupe(config_files),
        "dataset_hints": dedupe(dataset_hints),
        "metrics": dedupe(metrics),
        "artifacts": dedupe(artifacts),
        "large_files": dedupe(large_files[:10]),
        "paper_status": paper_status,
    }


def extract_overview(project_root: Path) -> str:
    for name in TOP_README_NAMES:
        candidate = project_root / name
        if candidate.exists():
            text = read_small_text(candidate)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if lines:
                return " ".join(lines[:6])
    return ""


def summarize_top_level(project_root: Path) -> list[str]:
    entries = []
    for path in sorted(project_root.iterdir(), key=lambda item: item.name.lower()):
        if path.name.lower() in {".git", ".idea", ".vscode", "__pycache__"}:
            continue
        entries.append(f"{path.name}/" if path.is_dir() else path.name)
    return entries[:20]


def summarize_result_file(path: Path, project_root: Path) -> str:
    suffix = path.suffix.lower()
    rel = normalize_relative(path, project_root)
    try:
        if suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            flat = flatten_json_metrics(data)
            if flat:
                compact = ", ".join(f"{key}={value}" for key, value in flat[:5])
                return f"`{rel}` -> {compact}"
        if suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                first_row = next(reader, None)
            if first_row:
                compact_items = []
                for key, value in first_row.items():
                    if len(compact_items) >= 4:
                        break
                    if value:
                        compact_items.append(f"{key}={value}")
                if compact_items:
                    return f"`{rel}` -> {', '.join(compact_items)}"
        if suffix in {".txt", ".log"} and any(token in rel.lower() for token in ("metric", "result", "train", "eval", "log")):
            text = read_small_text(path)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if lines:
                return f"`{rel}` -> {lines[-1][:140]}"
    except Exception:
        return ""
    return ""


def extract_dataset_hints(path: Path, project_root: Path, limit: int) -> list[str]:
    if limit <= 0:
        return []
    rel = normalize_relative(path, project_root)
    text = read_small_text(path)
    hints: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if any(keyword in lowered for keyword in TEXT_HINT_KEYWORDS):
            if len(line) > 160:
                line = line[:157] + "..."
            hints.append(f"`{rel}`: {line}")
        if len(hints) >= limit:
            break
    return hints


def summarize_paper_status(project_root: Path) -> list[str]:
    paper_dir = project_root / "paper"
    if not paper_dir.exists():
        return []
    items = [f"`paper/main.tex`: {'present' if (paper_dir / 'main.tex').exists() else 'missing'}"]
    snapshot = paper_dir / "context" / "project_snapshot.md"
    if snapshot.exists():
        items.append(f"`paper/context/project_snapshot.md`: updated {timestamp_text(snapshot)}")
    preview_pdf = paper_dir / "build" / "main_preview.pdf"
    if preview_pdf.exists():
        items.append(f"`paper/build/main_preview.pdf`: updated {timestamp_text(preview_pdf)}")
    log_path = paper_dir / "build" / "main.log"
    if log_path.exists():
        items.append(f"`paper/build/main.log`: updated {timestamp_text(log_path)}")
    return items


def timestamp_text(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def flatten_json_metrics(data, prefix: str = "") -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, (int, float, str)):
                items.append((next_prefix, str(value)))
            elif isinstance(value, (dict, list)):
                items.extend(flatten_json_metrics(value, next_prefix))
    elif isinstance(data, list):
        for index, value in enumerate(data[:3]):
            next_prefix = f"{prefix}[{index}]"
            if isinstance(value, (int, float, str)):
                items.append((next_prefix, str(value)))
            elif isinstance(value, (dict, list)):
                items.extend(flatten_json_metrics(value, next_prefix))
    return items[:10]


def format_large_file(rel_path: str, size_bytes: int) -> str:
    size_mb = size_bytes / (1024 * 1024)
    return f"`{rel_path}` ({size_mb:.1f} MB)"


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
