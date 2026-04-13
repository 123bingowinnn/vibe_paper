from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    paper_dir = Path(__file__).resolve().parents[1]
    project_root = paper_dir.parent
    vibe_paper_home = Path(r"__VIBE_PAPER_HOME__")
    unconfigured_vibe_paper_home = "__UNCONFIGURED_VIBE_PAPER_HOME__"
    if unconfigured_vibe_paper_home in str(vibe_paper_home):
        vibe_paper_home = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(vibe_paper_home))

    from core.cli import main as cli_main

    sys.argv = [
        "vibe-paper-build",
        "build",
        "--project-root",
        str(project_root),
    ]
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
