from __future__ import annotations

import argparse
from pathlib import Path

from .latex_runtime import compile_project_paper
from .paper_workspace import init_project_paper
from .project_context import write_project_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vibe Paper project runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create paper/ inside an experiment project")
    init_parser.add_argument("--project-root", required=True)
    init_parser.add_argument("--title")
    init_parser.add_argument("--author", default="Author Name")
    init_parser.add_argument("--affiliation", default="School / Department")
    init_parser.add_argument("--email", default="author@example.com")
    init_parser.add_argument("--force", action="store_true")

    scan_parser = subparsers.add_parser("scan", help="Regenerate paper/context/project_snapshot.md")
    scan_parser.add_argument("--project-root", required=True)

    build_parser_cmd = subparsers.add_parser("build", help="Compile paper/main.tex with the unified build backend")
    build_parser_cmd.add_argument("--project-root", required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if args.command == "init":
        paper_dir = init_project_paper(
            project_root=project_root,
            title=args.title,
            author=args.author,
            affiliation=args.affiliation,
            email=args.email,
            force=args.force,
        )
        snapshot_path = project_root / "paper" / "context" / "project_snapshot.md"
        print(f"Paper workspace created at: {paper_dir}")
        print(f"Snapshot generated at: {snapshot_path}")
        return 0

    if args.command == "scan":
        snapshot_path = write_project_snapshot(project_root)
        print(f"Snapshot updated: {snapshot_path}")
        return 0

    if args.command == "build":
        result = compile_project_paper(project_root)
        write_project_snapshot(project_root)
        print(result.message)
        print(result.log_text[-4000:])
        return 0 if result.success else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
