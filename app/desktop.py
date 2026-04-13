from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PyQt5.QtCore import QDir, Qt, QSize, QUrl
    from PyQt5.QtGui import QDesktopServices, QFont, QImage, QPixmap
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QFileSystemModel,
        QLabel,
        QDockWidget,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QScrollArea,
        QSizePolicy,
        QStatusBar,
        QToolBar,
        QTreeView,
        QVBoxLayout,
        QWidget,
    )
except ImportError as exc:  # pragma: no cover - import guard for end users
    raise SystemExit(
        "PyQt5 is required for the Vibe Paper desktop app. Install it and try again."
    ) from exc

from core.common import is_text_editable, normalize_relative
from core.latex_runtime import CompileResult, compile_project_paper
from core.pdf_preview import PdfPreviewError, render_pdf_preview_pages
from core.project_context import write_project_snapshot


TEXTS = {
    "en": {
        "windowTitle": "Vibe Paper Desktop",
        "files": "Project Files",
        "source": "Source Editor",
        "log": "Build Log",
        "generate": "Generate Context",
        "save": "Save File",
        "compile": "Compile Paper",
        "refresh": "Refresh Preview",
        "openFormal": "Open Formal PDF",
        "toggleFiles": "Files",
        "toggleSource": "Source",
        "toggleLog": "Log",
        "openFileHint": "Double-click a text file in the project tree to edit it here.",
        "noPreview": "No preview PDF is available yet. Compile the paper or refresh after LaTeX changes.",
        "contextDone": "Project snapshot regenerated.",
        "fileSaved": "File saved.",
        "compileDone": "Paper compiled successfully.",
        "compileFailed": "Paper compilation failed. The build log has been opened.",
        "previewDone": "Preview refreshed.",
        "fileNotEditable": "This file type is not editable in the built-in editor.",
        "previewError": "Preview refresh failed",
        "saveError": "Save failed",
        "compileError": "Compile failed",
        "contextError": "Context generation failed",
        "openPdfError": "Formal PDF is not available yet.",
        "lang": "中文",
        "statusReady": "Ready.",
    },
    "zh": {
        "windowTitle": "Vibe Paper 桌面版",
        "files": "项目文件",
        "source": "源码编辑器",
        "log": "编译日志",
        "generate": "生成上下文",
        "save": "保存文件",
        "compile": "编译论文",
        "refresh": "刷新预览",
        "openFormal": "打开正式 PDF",
        "toggleFiles": "目录",
        "toggleSource": "源码",
        "toggleLog": "日志",
        "openFileHint": "在左侧项目树中双击文本文件，就可以在这里编辑。",
        "noPreview": "还没有可用的预览 PDF。先编译论文，或在 LaTeX 修改后手动刷新。",
        "contextDone": "项目快照已重新生成。",
        "fileSaved": "文件已保存。",
        "compileDone": "论文编译成功。",
        "compileFailed": "论文编译失败，已自动打开编译日志面板。",
        "previewDone": "预览已刷新。",
        "fileNotEditable": "这种文件类型暂不支持在内置编辑器里修改。",
        "previewError": "预览刷新失败",
        "saveError": "保存失败",
        "compileError": "编译失败",
        "contextError": "上下文生成失败",
        "openPdfError": "正式 PDF 还不存在。",
        "lang": "EN",
        "statusReady": "已就绪。",
    },
}


class VibePaperDesktop(QMainWindow):
    def __init__(self, project_root: Path, language: str = "en") -> None:
        super().__init__()
        self.project_root = project_root.resolve()
        self.paper_dir = self.project_root / "paper"
        self.build_dir = self.paper_dir / "build"
        self.preview_pdf = self.build_dir / "main_preview.pdf"
        self.preview_image_dir = self.build_dir / ".preview_pages"
        self.language = language if language in TEXTS else "en"
        self.current_file: Path | None = None
        self.current_file_rel = ""
        self.page_pixmaps: list[QPixmap] = []
        self.page_labels: list[QLabel] = []

        self._build_ui()
        self._bind_actions()
        self._load_project_tree()
        self._load_default_file()
        self._apply_language()
        self.refresh_preview(show_message=False)

    def _build_ui(self) -> None:
        self.setMinimumSize(QSize(1100, 760))
        self.resize(1380, 920)

        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        self.toolbar = toolbar

        self.generate_action = QAction(self)
        self.save_action = QAction(self)
        self.compile_action = QAction(self)
        self.refresh_action = QAction(self)
        self.open_formal_action = QAction(self)
        self.toggle_files_action = QAction(self)
        self.toggle_source_action = QAction(self)
        self.toggle_log_action = QAction(self)
        self.lang_action = QAction(self)

        for action in (
            self.generate_action,
            self.save_action,
            self.compile_action,
            self.refresh_action,
            self.open_formal_action,
            self.toggle_files_action,
            self.toggle_source_action,
            self.toggle_log_action,
            self.lang_action,
        ):
            toolbar.addAction(action)

        self.preview_scroll = QScrollArea(self)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.preview_container = QWidget(self.preview_scroll)
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(18, 18, 18, 18)
        self.preview_layout.setSpacing(18)
        self.preview_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.preview_placeholder = QLabel(self.preview_container)
        self.preview_placeholder.setAlignment(Qt.AlignCenter)
        self.preview_placeholder.setWordWrap(True)
        self.preview_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        placeholder_font = QFont()
        placeholder_font.setPointSize(12)
        self.preview_placeholder.setFont(placeholder_font)
        self.preview_layout.addWidget(self.preview_placeholder)

        self.preview_scroll.setWidget(self.preview_container)
        self.setCentralWidget(self.preview_scroll)

        self.tree_model = QFileSystemModel(self)
        self.tree_model.setRootPath(str(self.project_root))
        self.tree_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.file_tree = QTreeView(self)
        self.file_tree.setModel(self.tree_model)
        self.file_tree.setRootIndex(self.tree_model.index(str(self.project_root)))
        self.file_tree.setHeaderHidden(False)
        self.file_tree.setAnimated(True)
        self.file_tree.setSortingEnabled(False)
        for column in range(1, 4):
            self.file_tree.hideColumn(column)
        self.file_tree.setMinimumWidth(260)

        self.file_dock = QDockWidget(self)
        self.file_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.file_dock.setWidget(self.file_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)

        self.editor_path_label = QLabel(self)
        self.editor_path_label.setWordWrap(True)
        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("")
        editor_container = QWidget(self)
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(6)
        editor_layout.addWidget(self.editor_path_label)
        editor_layout.addWidget(self.editor)

        self.editor_dock = QDockWidget(self)
        self.editor_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.editor_dock.setWidget(editor_container)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.editor_dock)
        self.tabifyDockWidget(self.file_dock, self.editor_dock)

        self.log_view = QPlainTextEdit(self)
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(2000)
        self.log_dock = QDockWidget(self)
        self.log_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.log_dock.setWidget(self.log_view)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        self.file_dock.hide()
        self.editor_dock.hide()
        self.log_dock.hide()

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def _bind_actions(self) -> None:
        self.generate_action.triggered.connect(self.generate_context)
        self.save_action.triggered.connect(self.save_current_file)
        self.compile_action.triggered.connect(self.compile_paper)
        self.refresh_action.triggered.connect(self.refresh_preview)
        self.open_formal_action.triggered.connect(self.open_formal_pdf)
        self.toggle_files_action.triggered.connect(self.toggle_files_panel)
        self.toggle_source_action.triggered.connect(self.toggle_source_panel)
        self.toggle_log_action.triggered.connect(self.toggle_log_panel)
        self.lang_action.triggered.connect(self.toggle_language)
        self.file_tree.doubleClicked.connect(self.open_selected_file)

    def _load_project_tree(self) -> None:
        self.tree_model.setRootPath(str(self.project_root))
        self.file_tree.setRootIndex(self.tree_model.index(str(self.project_root)))
        self.file_tree.expand(self.tree_model.index(str(self.paper_dir)))

    def _load_default_file(self) -> None:
        candidates = [
            self.paper_dir / "main.tex",
            self.paper_dir / "context" / "project_snapshot.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                self.load_file(candidate, show_panel=False)
                return
        self.editor_path_label.clear()
        self.editor.clear()

    def _apply_language(self) -> None:
        text = TEXTS[self.language]
        self.setWindowTitle(f"{text['windowTitle']} - {self.project_root.name}")
        self.generate_action.setText(text["generate"])
        self.save_action.setText(text["save"])
        self.compile_action.setText(text["compile"])
        self.refresh_action.setText(text["refresh"])
        self.open_formal_action.setText(text["openFormal"])
        self.toggle_files_action.setText(text["toggleFiles"])
        self.toggle_source_action.setText(text["toggleSource"])
        self.toggle_log_action.setText(text["toggleLog"])
        self.lang_action.setText(text["lang"])
        self.file_dock.setWindowTitle(text["files"])
        self.editor_dock.setWindowTitle(text["source"])
        self.log_dock.setWindowTitle(text["log"])
        if not self.current_file:
            self.editor_path_label.setText(text["openFileHint"])
        self.status_bar.showMessage(text["statusReady"], 2500)
        if not self.page_pixmaps:
            self.preview_placeholder.setText(text["noPreview"])

    def toggle_language(self) -> None:
        self.language = "zh" if self.language == "en" else "en"
        self._apply_language()

    def toggle_files_panel(self) -> None:
        self.file_dock.setVisible(not self.file_dock.isVisible())

    def toggle_source_panel(self) -> None:
        self.editor_dock.setVisible(not self.editor_dock.isVisible())

    def toggle_log_panel(self) -> None:
        self.log_dock.setVisible(not self.log_dock.isVisible())

    def open_selected_file(self, index) -> None:
        path = Path(self.tree_model.filePath(index))
        if path.is_dir():
            return
        self.load_file(path, show_panel=True)

    def load_file(self, path: Path, show_panel: bool = True) -> None:
        if not is_text_editable(path):
            self._show_status(TEXTS[self.language]["fileNotEditable"])
            return
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self._show_error(TEXTS[self.language]["saveError"], str(exc))
            return

        self.current_file = path.resolve()
        self.current_file_rel = normalize_relative(self.current_file, self.project_root)
        self.editor.blockSignals(True)
        self.editor.setPlainText(content)
        self.editor.blockSignals(False)
        self.editor.document().setModified(False)
        self.editor_path_label.setText(self.current_file_rel)
        if show_panel:
            self.editor_dock.show()
            self.raise_()

    def save_current_file(self) -> bool:
        if not self.current_file:
            self._show_status(TEXTS[self.language]["openFileHint"])
            return False
        try:
            self.current_file.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            self._show_error(TEXTS[self.language]["saveError"], str(exc))
            return False
        self.editor.document().setModified(False)
        self._show_status(TEXTS[self.language]["fileSaved"])
        return True

    def generate_context(self) -> None:
        try:
            snapshot = write_project_snapshot(self.project_root)
        except Exception as exc:  # pragma: no cover - runtime error path
            self._show_error(TEXTS[self.language]["contextError"], str(exc))
            return
        self._load_project_tree()
        if self.current_file and self.current_file.resolve() == snapshot.resolve():
            self.load_file(snapshot, show_panel=self.editor_dock.isVisible())
        self._show_status(TEXTS[self.language]["contextDone"])

    def compile_paper(self) -> None:
        if self.current_file and self.editor.document().isModified():
            if not self.save_current_file():
                return
        result = compile_project_paper(self.project_root)
        try:
            write_project_snapshot(self.project_root)
        except Exception:
            pass
        self.log_view.setPlainText(result.log_text)
        if result.success:
            self.refresh_preview(show_message=False)
            self._show_status(TEXTS[self.language]["compileDone"])
        else:
            self.log_dock.show()
            self._show_error(TEXTS[self.language]["compileError"], result.message)
            self.status_bar.showMessage(TEXTS[self.language]["compileFailed"], 5000)
        self._load_project_tree()

    def refresh_preview(self, show_message: bool = True) -> None:
        self.preview_placeholder.show()
        self.preview_placeholder.setText(TEXTS[self.language]["noPreview"])
        if not self.preview_pdf.exists():
            self._clear_preview_pages()
            if show_message:
                self._show_status(TEXTS[self.language]["noPreview"])
            return

        try:
            page_paths = render_pdf_preview_pages(self.preview_pdf, self.preview_image_dir)
        except PdfPreviewError as exc:
            self._clear_preview_pages()
            self._show_error(TEXTS[self.language]["previewError"], str(exc))
            return

        self._clear_preview_pages()
        self.page_pixmaps = []
        self.page_labels = []
        self.preview_placeholder.hide()

        for page_path in page_paths:
            image = QImage(str(page_path))
            if image.isNull():
                continue
            pixmap = QPixmap.fromImage(image)
            label = QLabel(self.preview_container)
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.preview_layout.addWidget(label)
            self.page_pixmaps.append(pixmap)
            self.page_labels.append(label)

        self._rescale_preview_pages()
        if show_message:
            self._show_status(TEXTS[self.language]["previewDone"])

    def open_formal_pdf(self) -> None:
        formal_pdf = self.build_dir / "main.pdf"
        if not formal_pdf.exists():
            self._show_status(TEXTS[self.language]["openPdfError"])
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(formal_pdf)))

    def _clear_preview_pages(self) -> None:
        for label in self.page_labels:
            self.preview_layout.removeWidget(label)
            label.deleteLater()
        self.page_labels = []
        self.page_pixmaps = []

    def _rescale_preview_pages(self) -> None:
        if not self.page_pixmaps or not self.page_labels:
            return
        viewport_width = max(300, self.preview_scroll.viewport().width() - 56)
        for pixmap, label in zip(self.page_pixmaps, self.page_labels):
            scaled = pixmap.scaledToWidth(viewport_width, Qt.SmoothTransformation)
            label.setPixmap(scaled)
            label.setMinimumHeight(scaled.height())

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._rescale_preview_pages()

    def _show_status(self, message: str) -> None:
        self.status_bar.showMessage(message, 3500)

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)


def run_smoke_test(project_root: Path) -> int:
    project_root = project_root.resolve()
    write_project_snapshot(project_root)
    result: CompileResult = compile_project_paper(project_root)
    if not result.success:
        print(result.log_text)
        return 1
    pages = render_pdf_preview_pages(
        project_root / "paper" / "build" / "main_preview.pdf",
        project_root / "paper" / "build" / ".preview_smoke",
    )
    print(f"Compiled successfully and rendered {len(pages)} preview page(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Vibe Paper desktop app")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--lang", choices=("en", "zh"), default="en")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if args.smoke_test:
        return run_smoke_test(project_root)

    app = QApplication([])
    app.setApplicationName("Vibe Paper")
    window = VibePaperDesktop(project_root=project_root, language=args.lang)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
