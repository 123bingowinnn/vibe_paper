from __future__ import annotations

import argparse
import webbrowser
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_file

from core.common import build_tree, is_text_editable, normalize_relative, read_small_text, resolve_within_root
from core.latex_runtime import compile_project_paper
from core.project_context import summarize_paper_status, write_project_snapshot


def create_app(project_root: Path) -> Flask:
    project_root = project_root.resolve()
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().parent / "templates"),
        static_folder=str(Path(__file__).resolve().parent / "static"),
    )

    @app.route("/")
    def index():
        return render_template("index.html", project_name=project_root.name)

    @app.route("/api/bootstrap")
    def bootstrap():
        snapshot_path = project_root / "paper" / "context" / "project_snapshot.md"
        default_file = "paper/main.tex" if (project_root / "paper" / "main.tex").exists() else None
        if not default_file and snapshot_path.exists():
            default_file = "paper/context/project_snapshot.md"
        return jsonify(
            {
                "projectName": project_root.name,
                "tree": build_tree(project_root),
                "defaultFile": default_file,
                "snapshotPath": "paper/context/project_snapshot.md" if snapshot_path.exists() else None,
                "paperStatus": summarize_paper_status(project_root),
            }
        )

    @app.route("/api/file")
    def get_file():
        rel_path = request.args.get("path", "")
        path = resolve_within_root(project_root, rel_path)
        if not path.exists():
            abort(404, "File not found.")
        if path.is_dir():
            abort(400, "Directories cannot be opened in the editor.")
        if not is_text_editable(path):
            return jsonify(
                {
                    "path": normalize_relative(path, project_root),
                    "editable": False,
                    "content": "",
                    "mtime": int(path.stat().st_mtime),
                    "message": "This file type is not editable in the built-in editor.",
                }
            )
        return jsonify(
            {
                "path": normalize_relative(path, project_root),
                "editable": True,
                "content": read_small_text(path),
                "mtime": int(path.stat().st_mtime),
            }
        )

    @app.route("/api/file", methods=["POST"])
    def save_file():
        payload = request.get_json(force=True)
        rel_path = payload.get("path", "")
        content = payload.get("content", "")
        path = resolve_within_root(project_root, rel_path)
        if not is_text_editable(path):
            abort(400, "This file type is not editable.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return jsonify(
            {
                "path": normalize_relative(path, project_root),
                "mtime": int(path.stat().st_mtime),
            }
        )

    @app.route("/api/context/regenerate", methods=["POST"])
    def regenerate_context():
        snapshot = write_project_snapshot(project_root)
        return jsonify(
            {
                "snapshotPath": normalize_relative(snapshot, project_root),
                "mtime": int(snapshot.stat().st_mtime),
                "tree": build_tree(project_root),
            }
        )

    @app.route("/api/compile", methods=["POST"])
    def compile_paper():
        result = compile_project_paper(project_root)
        write_project_snapshot(project_root)
        response = result.to_dict()
        response["paperStatus"] = summarize_paper_status(project_root)
        response["tree"] = build_tree(project_root)
        return jsonify(response)

    @app.route("/api/state")
    def state():
        active_path = request.args.get("path")
        active_mtime = None
        if active_path:
            try:
                active_file = resolve_within_root(project_root, active_path)
                if active_file.exists():
                    active_mtime = int(active_file.stat().st_mtime)
            except ValueError:
                active_mtime = None
        preview_path = project_root / "paper" / "build" / "main_preview.pdf"
        log_path = project_root / "paper" / "build" / "main.log"
        snapshot_path = project_root / "paper" / "context" / "project_snapshot.md"
        payload = {
            "activePathMtime": active_mtime,
            "previewExists": preview_path.exists(),
            "previewMtime": int(preview_path.stat().st_mtime) if preview_path.exists() else None,
            "snapshotMtime": int(snapshot_path.stat().st_mtime) if snapshot_path.exists() else None,
            "logExcerpt": tail_text(log_path, 40),
        }
        return jsonify(payload)

    @app.route("/pdf/preview")
    def preview_pdf():
        preview_path = project_root / "paper" / "build" / "main_preview.pdf"
        if not preview_path.exists():
            abort(404, "Preview PDF is not available yet.")
        return send_file(preview_path, mimetype="application/pdf")

    @app.route("/pdf/formal")
    def formal_pdf():
        formal_path = project_root / "paper" / "build" / "main.pdf"
        if not formal_path.exists():
            abort(404, "Formal PDF is not available yet.")
        return send_file(formal_path, mimetype="application/pdf")

    @app.route("/api/project-metadata")
    def project_metadata():
        return jsonify(
            {
                "projectRoot": str(project_root),
                "paperExists": (project_root / "paper").exists(),
                "paperStatus": summarize_paper_status(project_root),
            }
        )

    return app


def tail_text(path: Path, max_lines: int) -> str:
    if not path.exists():
        return ""
    text = read_small_text(path)
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-max_lines:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Vibe Paper local web app")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    app = create_app(project_root)
    if args.open_browser:
        webbrowser.open(f"http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
