from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PyQt5.QtCore import QDir, Qt, QSize, QTimer, QUrl
    from PyQt5.QtGui import QColor, QDesktopServices, QFont, QImage, QPixmap
    from PyQt5.QtWidgets import (
        QApplication,
        QDockWidget,
        QFileSystemModel,
        QFrame,
        QGraphicsDropShadowEffect,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QStatusBar,
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
        "windowTitle": "Vibe Paper",
        "files": "Files",
        "source": "Source",
        "log": "Log",
        "generate": "Context",
        "save": "Save",
        "compile": "Compile",
        "refresh": "Refresh",
        "openFormal": "Open PDF",
        "pathPrefix": "Current file",
        "noPreview": "No preview PDF is available yet. Compile the paper or refresh after LaTeX changes.",
        "contextDone": "Project snapshot regenerated.",
        "fileSaved": "File saved.",
        "compileDone": "Paper compiled successfully.",
        "compileFailed": "Paper compilation failed. Open the log panel for details.",
        "previewDone": "Preview refreshed.",
        "fileNotEditable": "This file type is not editable in the built-in editor.",
        "previewError": "Preview refresh failed",
        "saveError": "Save failed",
        "compileError": "Compile failed",
        "contextError": "Context generation failed",
        "openPdfError": "Formal PDF is not available yet.",
        "lang": "中文",
        "statusReady": "Ready",
        "hint": "Preview-first mode",
    },
    "zh": {
        "windowTitle": "Vibe Paper",
        "files": "目录",
        "source": "源码",
        "log": "日志",
        "generate": "上下文",
        "save": "保存",
        "compile": "编译",
        "refresh": "刷新",
        "openFormal": "PDF",
        "pathPrefix": "当前文件",
        "noPreview": "还没有可用的预览 PDF。先编译论文，或在 LaTeX 修改后手动刷新。",
        "contextDone": "项目快照已重新生成。",
        "fileSaved": "文件已保存。",
        "compileDone": "论文编译成功。",
        "compileFailed": "论文编译失败，请展开日志面板查看详细信息。",
        "previewDone": "预览已刷新。",
        "fileNotEditable": "这种文件类型暂不支持在内置编辑器里修改。",
        "previewError": "预览刷新失败",
        "saveError": "保存失败",
        "compileError": "编译失败",
        "contextError": "上下文生成失败",
        "openPdfError": "正式 PDF 还不存在。",
        "lang": "EN",
        "statusReady": "已就绪",
        "hint": "预览优先模式",
    },
}


APP_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(229, 236, 248, 255),
        stop:0.58 rgba(238, 243, 250, 255),
        stop:1 rgba(228, 235, 245, 255));
}
QFrame#OverlayBar {
    background: rgba(255, 255, 255, 146);
    border: 1px solid rgba(255, 255, 255, 176);
    border-radius: 17px;
}
QFrame#PageFrame {
    background: rgba(255, 255, 255, 242);
    border: 1px solid rgba(255, 255, 255, 214);
    border-radius: 22px;
}
QLabel#BrandLabel {
    color: #172233;
    font-size: 13px;
    font-weight: 700;
}
QLabel#MetaLabel {
    color: rgba(44, 58, 78, 172);
    font-size: 11px;
}
QLabel#PageHintLabel,
QLabel#PathLabel {
    color: rgba(55, 68, 88, 158);
    font-size: 11px;
}
QPushButton {
    min-height: 28px;
    padding: 0 10px;
    border-radius: 13px;
    border: 1px solid rgba(255, 255, 255, 176);
    background: rgba(255, 255, 255, 118);
    color: #213048;
    font-size: 11px;
    font-weight: 600;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 158);
    border-color: rgba(255, 255, 255, 214);
}
QPushButton:pressed {
    background: rgba(230, 237, 248, 176);
}
QPushButton[accent="true"] {
    background: rgba(61, 107, 224, 214);
    border: 1px solid rgba(61, 107, 224, 228);
    color: white;
}
QPushButton[accent="true"]:hover {
    background: rgba(47, 90, 202, 228);
}
QPushButton[toggleButton="true"]:checked {
    background: rgba(235, 242, 255, 172);
    border-color: rgba(170, 194, 244, 206);
    color: #244aa5;
}
QDockWidget {
    color: #1f2b3a;
}
QDockWidget::title {
    text-align: left;
    padding-left: 12px;
    height: 28px;
    background: rgba(255, 255, 255, 176);
    border: 1px solid rgba(255, 255, 255, 185);
    border-radius: 12px;
    color: #243145;
    font-weight: 600;
}
QTreeView,
QPlainTextEdit {
    background: rgba(255, 255, 255, 148);
    border: 1px solid rgba(255, 255, 255, 182);
    border-radius: 14px;
    color: #1f2b3a;
    selection-background-color: #dfeaff;
    selection-color: #1f2b3a;
}
QTreeView {
    padding: 8px;
}
QTreeView::item {
    padding: 6px 4px;
    border-radius: 8px;
}
QTreeView::item:hover {
    background: rgba(240, 245, 253, 225);
}
QPlainTextEdit {
    padding: 10px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QStatusBar {
    background: transparent;
    color: rgba(57, 71, 92, 180);
}
"""


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
        self.page_frames: list[QFrame] = []
        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self._reset_header_status)

        self._build_ui()
        self._bind_actions()
        self._load_project_tree()
        self._load_default_file()
        self._apply_language()
        self.refresh_preview(show_message=False)

    def _build_ui(self) -> None:
        self.setMinimumSize(QSize(1180, 760))
        self.resize(1450, 930)
        self.setStyleSheet(APP_STYLESHEET)

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 6)
        root_layout.setSpacing(0)

        self.overlay_bar = QFrame(central)
        self.overlay_bar.setObjectName("OverlayBar")
        self._apply_shadow(self.overlay_bar, blur=24, alpha=28, offset_y=4)
        overlay_layout = QHBoxLayout(self.overlay_bar)
        overlay_layout.setContentsMargins(14, 6, 14, 6)
        overlay_layout.setSpacing(8)

        self.brand_label = QLabel(self.overlay_bar)
        self.brand_label.setObjectName("BrandLabel")
        self.meta_label = QLabel(self.overlay_bar)
        self.meta_label.setObjectName("MetaLabel")
        overlay_layout.addWidget(self.brand_label)
        overlay_layout.addWidget(self.meta_label)
        overlay_layout.addStretch(1)

        self.generate_button = self._make_button(accent=False)
        self.save_button = self._make_button(accent=False)
        self.compile_button = self._make_button(accent=True)
        self.refresh_button = self._make_button(accent=False)
        self.open_formal_button = self._make_button(accent=False)
        self.files_button = self._make_button(toggle=True)
        self.source_button = self._make_button(toggle=True)
        self.log_button = self._make_button(toggle=True)
        self.lang_button = self._make_button(accent=False)

        for button in (
            self.generate_button,
            self.save_button,
            self.compile_button,
            self.refresh_button,
            self.open_formal_button,
            self.files_button,
            self.source_button,
            self.log_button,
            self.lang_button,
        ):
            overlay_layout.addWidget(button)

        self.preview_scroll = QScrollArea(self)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.preview_container = QWidget(self.preview_scroll)
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(6, 60, 6, 20)
        self.preview_layout.setSpacing(20)
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

        root_layout.addWidget(self.preview_scroll, 1)
        self.setCentralWidget(central)
        self.overlay_bar.raise_()

        self.tree_model = QFileSystemModel(self)
        self.tree_model.setRootPath(str(self.project_root))
        self.tree_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.file_tree = QTreeView(self)
        self.file_tree.setModel(self.tree_model)
        self.file_tree.setRootIndex(self.tree_model.index(str(self.project_root)))
        self.file_tree.setHeaderHidden(False)
        self.file_tree.setAnimated(True)
        for column in range(1, 4):
            self.file_tree.hideColumn(column)
        self.file_tree.setMinimumWidth(260)

        self.file_dock = QDockWidget(self)
        self.file_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.file_dock.setWidget(self.file_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)

        self.path_label = QLabel(self)
        self.path_label.setObjectName("PathLabel")
        self.path_label.setWordWrap(True)
        self.editor = QPlainTextEdit(self)
        editor_container = QWidget(self)
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(8)
        editor_layout.addWidget(self.path_label)
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
        self.status_bar.setSizeGripEnabled(False)
        self.setStatusBar(self.status_bar)

    def _bind_actions(self) -> None:
        self.generate_button.clicked.connect(self.generate_context)
        self.save_button.clicked.connect(self.save_current_file)
        self.compile_button.clicked.connect(self.compile_paper)
        self.refresh_button.clicked.connect(self.refresh_preview)
        self.open_formal_button.clicked.connect(self.open_formal_pdf)
        self.files_button.clicked.connect(self.toggle_files_panel)
        self.source_button.clicked.connect(self.toggle_source_panel)
        self.log_button.clicked.connect(self.toggle_log_panel)
        self.lang_button.clicked.connect(self.toggle_language)
        self.file_tree.doubleClicked.connect(self.open_selected_file)
        self.file_dock.visibilityChanged.connect(self._sync_toggle_buttons)
        self.editor_dock.visibilityChanged.connect(self._sync_toggle_buttons)
        self.log_dock.visibilityChanged.connect(self._sync_toggle_buttons)

    def _load_project_tree(self) -> None:
        self.tree_model.setRootPath(str(self.project_root))
        self.file_tree.setRootIndex(self.tree_model.index(str(self.project_root)))
        paper_index = self.tree_model.index(str(self.paper_dir))
        if paper_index.isValid():
            self.file_tree.expand(paper_index)

    def _load_default_file(self) -> None:
        candidates = [
            self.paper_dir / "main.tex",
            self.paper_dir / "context" / "project_snapshot.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                self.load_file(candidate, show_panel=False)
                return
        self.path_label.clear()
        self.editor.clear()

    def _apply_language(self) -> None:
        text = TEXTS[self.language]
        self.setWindowTitle(f"{text['windowTitle']} - {self.project_root.name}")
        self.brand_label.setText("Vibe Paper")
        self._reset_header_status()

        self.generate_button.setText(text["generate"])
        self.save_button.setText(text["save"])
        self.compile_button.setText(text["compile"])
        self.refresh_button.setText(text["refresh"])
        self.open_formal_button.setText(text["openFormal"])
        self.files_button.setText(text["files"])
        self.source_button.setText(text["source"])
        self.log_button.setText(text["log"])
        self.lang_button.setText(text["lang"])

        self.file_dock.setWindowTitle(text["files"])
        self.editor_dock.setWindowTitle(text["source"])
        self.log_dock.setWindowTitle(text["log"])

        if self.current_file_rel:
            self.path_label.setText(f"{text['pathPrefix']}: {self.current_file_rel}")
        else:
            self.path_label.clear()

        if not self.page_frames:
            self.preview_placeholder.setText(text["noPreview"])

        self._sync_toggle_buttons()

    def _make_button(self, accent: bool = False, toggle: bool = False) -> QPushButton:
        button = QPushButton(self.overlay_bar)
        if accent:
            button.setProperty("accent", True)
        if toggle:
            button.setCheckable(True)
            button.setProperty("toggleButton", True)
        button.setCursor(Qt.PointingHandCursor)
        button.style().unpolish(button)
        button.style().polish(button)
        return button

    def _apply_shadow(
        self,
        widget: QWidget,
        blur: int = 24,
        alpha: int = 34,
        offset_x: int = 0,
        offset_y: int = 8,
    ) -> None:
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(offset_x, offset_y)
        shadow.setColor(QColor(19, 33, 54, alpha))
        widget.setGraphicsEffect(shadow)

    def _sync_toggle_buttons(self) -> None:
        self.files_button.blockSignals(True)
        self.source_button.blockSignals(True)
        self.log_button.blockSignals(True)
        self.files_button.setChecked(self.file_dock.isVisible())
        self.source_button.setChecked(self.editor_dock.isVisible())
        self.log_button.setChecked(self.log_dock.isVisible())
        self.files_button.blockSignals(False)
        self.source_button.blockSignals(False)
        self.log_button.blockSignals(False)

    def toggle_files_panel(self) -> None:
        self.file_dock.setVisible(not self.file_dock.isVisible())
        self._sync_toggle_buttons()

    def toggle_source_panel(self) -> None:
        self.editor_dock.setVisible(not self.editor_dock.isVisible())
        self._sync_toggle_buttons()

    def toggle_log_panel(self) -> None:
        self.log_dock.setVisible(not self.log_dock.isVisible())
        self._sync_toggle_buttons()

    def toggle_language(self) -> None:
        self.language = "zh" if self.language == "en" else "en"
        self._apply_language()

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
        self.path_label.setText(f"{TEXTS[self.language]['pathPrefix']}: {self.current_file_rel}")
        if show_panel:
            self.editor_dock.show()
            self.raiseDockWidget(self.editor_dock)
            self._sync_toggle_buttons()

    def raiseDockWidget(self, dock: QDockWidget) -> None:  # noqa: N802 - Qt-ish helper
        dock.raise_()
        dock.activateWindow()

    def save_current_file(self) -> bool:
        if not self.current_file:
            self._show_status(TEXTS[self.language]["source"])
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
        self._show_status(TEXTS[self.language]["compile"])
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
            self._sync_toggle_buttons()
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
        self.preview_placeholder.hide()

        for page_number, page_path in enumerate(page_paths, start=1):
            image = QImage(str(page_path))
            if image.isNull():
                continue
            pixmap = QPixmap.fromImage(image)

            page_frame = QFrame(self.preview_container)
            page_frame.setObjectName("PageFrame")
            self._apply_shadow(page_frame, blur=24, alpha=28, offset_y=8)
            page_layout = QVBoxLayout(page_frame)
            page_layout.setContentsMargins(18, 16, 18, 18)
            page_layout.setSpacing(8)

            page_hint = QLabel(f"Page {page_number}", page_frame)
            page_hint.setObjectName("PageHintLabel")
            page_hint.setAlignment(Qt.AlignCenter)
            page_hint.setVisible(len(page_paths) > 1)

            page_label = QLabel(page_frame)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            page_layout.addWidget(page_hint)
            page_layout.addWidget(page_label)
            self.preview_layout.addWidget(page_frame)

            page_frame._page_label = page_label  # type: ignore[attr-defined]
            self.page_frames.append(page_frame)
            self.page_pixmaps.append(pixmap)

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
        for page_frame in self.page_frames:
            self.preview_layout.removeWidget(page_frame)
            page_frame.deleteLater()
        self.page_frames = []
        self.page_pixmaps = []

    def _rescale_preview_pages(self) -> None:
        if not self.page_pixmaps or not self.page_frames:
            return
        viewport_width = max(440, self.preview_scroll.viewport().width() - 70)
        for pixmap, page_frame in zip(self.page_pixmaps, self.page_frames):
            page_label = page_frame._page_label  # type: ignore[attr-defined]
            scaled = pixmap.scaledToWidth(viewport_width, Qt.SmoothTransformation)
            page_label.setPixmap(scaled)
            page_label.setMinimumHeight(scaled.height())

    def _position_overlay_bar(self) -> None:
        margin = 12
        max_width = max(620, self.centralWidget().width() - margin * 2)
        desired = min(max_width, self.overlay_bar.sizeHint().width())
        height = self.overlay_bar.sizeHint().height()
        x = max(margin, (self.centralWidget().width() - desired) // 2)
        self.overlay_bar.setGeometry(x, margin, desired, height)
        self.overlay_bar.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._position_overlay_bar()
        self._rescale_preview_pages()

    def _reset_header_status(self) -> None:
        text = TEXTS[self.language]
        self.meta_label.setText(f"{self.project_root.name} · {text['hint']} · {text['statusReady']}")

    def _show_status(self, message: str) -> None:
        self.meta_label.setText(f"{self.project_root.name} · {message}")
        self.status_bar.showMessage(message, 3200)
        self.status_timer.start(3200)

    def _show_error(self, title: str, message: str) -> None:
        self.meta_label.setText(f"{self.project_root.name} · {title}")
        self.status_timer.start(4000)
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
