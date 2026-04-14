from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PyQt5.QtCore import QDir, QSize, Qt, QTimer, QUrl
    from PyQt5.QtGui import QColor, QDesktopServices, QFont, QImage, QKeySequence, QPixmap
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
        QShortcut,
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
        "compile": "Update",
        "openFormal": "PDF",
        "lang": "中",
        "pathPrefix": "Current file",
        "statusReady": "Ready",
        "statusPreview": "Preview-only",
        "statusCompiling": "Updating",
        "statusNoPreview": "No preview yet",
        "noPreview": "No preview PDF is available yet. Use Update after LaTeX changes.",
        "contextDone": "Project snapshot regenerated.",
        "fileSaved": "File saved.",
        "compileDone": "Paper compiled successfully.",
        "compileFailed": "Paper compilation failed. Open the log panel for details.",
        "previewDone": "Preview updated.",
        "fileNotEditable": "This file type is not editable in the built-in editor.",
        "previewError": "Preview update failed",
        "saveError": "Save failed",
        "compileError": "Compile failed",
        "contextError": "Context generation failed",
        "openPdfError": "Formal PDF is not available yet.",
    },
    "zh": {
        "windowTitle": "Vibe Paper",
        "files": "目录",
        "source": "源码",
        "log": "日志",
        "compile": "更新",
        "openFormal": "PDF",
        "lang": "EN",
        "pathPrefix": "当前文件",
        "statusReady": "已就绪",
        "statusPreview": "预览优先",
        "statusCompiling": "更新中",
        "statusNoPreview": "暂无预览",
        "noPreview": "还没有可用的预览 PDF。修改 LaTeX 后点一次更新即可。",
        "contextDone": "项目快照已重新生成。",
        "fileSaved": "文件已保存。",
        "compileDone": "论文编译成功。",
        "compileFailed": "论文编译失败，请展开日志面板查看详细信息。",
        "previewDone": "预览已更新。",
        "fileNotEditable": "这种文件类型暂不支持在内置编辑器里修改。",
        "previewError": "预览更新失败",
        "saveError": "保存失败",
        "compileError": "编译失败",
        "contextError": "上下文生成失败",
        "openPdfError": "正式 PDF 还不存在。",
    },
}


APP_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(232, 238, 247, 255),
        stop:0.56 rgba(241, 245, 251, 255),
        stop:1 rgba(230, 236, 245, 255));
}
QFrame#OverlayBar {
    background: rgba(255, 255, 255, 128);
    border: 1px solid rgba(255, 255, 255, 156);
    border-radius: 14px;
}
QFrame#BusyOverlay {
    background: rgba(234, 240, 249, 148);
    border-radius: 18px;
}
QLabel#BusyChip {
    padding: 3px 10px;
    border-radius: 11px;
    background: rgba(67, 109, 225, 46);
    border: 1px solid rgba(67, 109, 225, 108);
    color: #2f58bf;
    font-size: 10px;
    font-weight: 700;
}
QFrame#BusyCard {
    background: rgba(255, 255, 255, 212);
    border: 1px solid rgba(255, 255, 255, 226);
    border-radius: 18px;
}
QLabel#BusyTitle {
    color: #20469f;
    font-size: 16px;
    font-weight: 700;
}
QLabel#BusyBody {
    color: rgba(43, 58, 82, 186);
    font-size: 11px;
}
QFrame#PageFrame {
    background: rgba(255, 255, 255, 242);
    border: 1px solid rgba(255, 255, 255, 214);
    border-radius: 20px;
}
QLabel#BrandLabel {
    color: #162338;
    font-size: 12px;
    font-weight: 700;
}
QLabel#MetaLabel {
    color: rgba(47, 60, 82, 148);
    font-size: 10px;
}
QLabel#PageHintLabel,
QLabel#PathLabel {
    color: rgba(55, 68, 88, 148);
    font-size: 11px;
}
QPushButton {
    min-height: 24px;
    padding: 0 9px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 166);
    background: rgba(255, 255, 255, 100);
    color: #223047;
    font-size: 10px;
    font-weight: 600;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 144);
    border-color: rgba(255, 255, 255, 206);
}
QPushButton:pressed {
    background: rgba(232, 238, 248, 152);
}
QPushButton[accent="true"] {
    background: rgba(68, 109, 225, 204);
    border: 1px solid rgba(68, 109, 225, 216);
    color: white;
}
QPushButton[accent="true"]:hover {
    background: rgba(54, 95, 209, 222);
}
QDockWidget {
    color: #1f2b3a;
}
QDockWidget::title {
    text-align: left;
    padding-left: 12px;
    height: 28px;
    background: rgba(255, 255, 255, 174);
    border: 1px solid rgba(255, 255, 255, 184);
    border-radius: 12px;
    color: #243145;
    font-weight: 600;
}
QTreeView,
QPlainTextEdit {
    background: rgba(255, 255, 255, 146);
    border: 1px solid rgba(255, 255, 255, 180);
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
    color: rgba(57, 71, 92, 176);
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
        self._apply_shadow(self.overlay_bar, blur=22, alpha=24, offset_y=4)
        overlay_layout = QHBoxLayout(self.overlay_bar)
        overlay_layout.setContentsMargins(12, 5, 12, 5)
        overlay_layout.setSpacing(7)

        self.brand_label = QLabel(self.overlay_bar)
        self.brand_label.setObjectName("BrandLabel")
        self.meta_label = QLabel(self.overlay_bar)
        self.meta_label.setObjectName("MetaLabel")
        overlay_layout.addWidget(self.brand_label)
        overlay_layout.addWidget(self.meta_label)
        overlay_layout.addStretch(1)

        self.busy_chip = QLabel(self.overlay_bar)
        self.busy_chip.setObjectName("BusyChip")
        self.busy_chip.hide()
        overlay_layout.addWidget(self.busy_chip)

        self.compile_button = self._make_button(accent=True)
        self.open_formal_button = self._make_button()
        self.files_button = self._make_button()
        self.lang_button = self._make_button()

        for button in (
            self.compile_button,
            self.open_formal_button,
            self.files_button,
            self.lang_button,
        ):
            overlay_layout.addWidget(button)

        self.preview_scroll = QScrollArea(self)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.preview_container = QWidget(self.preview_scroll)
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(6, 48, 6, 16)
        self.preview_layout.setSpacing(16)
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

        self.preview_busy_overlay = QFrame(self.preview_scroll.viewport())
        self.preview_busy_overlay.setObjectName("BusyOverlay")
        self.preview_busy_overlay.hide()

        busy_overlay_layout = QVBoxLayout(self.preview_busy_overlay)
        busy_overlay_layout.setContentsMargins(0, 0, 0, 0)
        busy_overlay_layout.setAlignment(Qt.AlignCenter)

        self.busy_card = QFrame(self.preview_busy_overlay)
        self.busy_card.setObjectName("BusyCard")
        self._apply_shadow(self.busy_card, blur=24, alpha=24, offset_y=6)
        busy_card_layout = QVBoxLayout(self.busy_card)
        busy_card_layout.setContentsMargins(22, 18, 22, 18)
        busy_card_layout.setSpacing(6)

        self.busy_title = QLabel(self.busy_card)
        self.busy_title.setObjectName("BusyTitle")
        self.busy_title.setAlignment(Qt.AlignCenter)
        self.busy_body = QLabel(self.busy_card)
        self.busy_body.setObjectName("BusyBody")
        self.busy_body.setAlignment(Qt.AlignCenter)

        busy_card_layout.addWidget(self.busy_title)
        busy_card_layout.addWidget(self.busy_body)
        busy_overlay_layout.addWidget(self.busy_card)

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
        self.compile_button.clicked.connect(self.compile_paper)
        self.open_formal_button.clicked.connect(self.open_formal_pdf)
        self.files_button.clicked.connect(self.toggle_files_panel)
        self.lang_button.clicked.connect(self.toggle_language)
        self.file_tree.doubleClicked.connect(self.open_selected_file)
        self._bind_shortcuts()

    def _bind_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.compile_paper)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, activated=self.open_formal_pdf)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save_current_file)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=self.toggle_files_panel)
        QShortcut(QKeySequence("Ctrl+2"), self, activated=self.toggle_source_panel)
        QShortcut(QKeySequence("Ctrl+3"), self, activated=self.toggle_log_panel)
        QShortcut(QKeySequence("Ctrl+Shift+G"), self, activated=self.generate_context)

    def _load_project_tree(self) -> None:
        self.tree_model.setRootPath(str(self.project_root))
        self.file_tree.setRootIndex(self.tree_model.index(str(self.project_root)))
        paper_index = self.tree_model.index(str(self.paper_dir))
        if paper_index.isValid():
            self.file_tree.expand(paper_index)

    def _load_default_file(self) -> None:
        for candidate in (
            self.paper_dir / "main.tex",
            self.paper_dir / "context" / "project_snapshot.md",
        ):
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

        self.compile_button.setText(text["compile"])
        self.open_formal_button.setText(text["openFormal"])
        self.files_button.setText(text["files"])
        self.lang_button.setText(text["lang"])

        self.compile_button.setToolTip(f"{text['compile']} (Ctrl+Enter)")
        self.open_formal_button.setToolTip(f"{text['openFormal']} (Ctrl+Shift+O)")
        self.files_button.setToolTip(f"{text['files']} (Ctrl+1)")
        self.lang_button.setToolTip(f"{text['source']}: Ctrl+2 | {text['log']}: Ctrl+3")

        self.file_dock.setWindowTitle(text["files"])
        self.editor_dock.setWindowTitle(text["source"])
        self.log_dock.setWindowTitle(text["log"])

        if self.current_file_rel:
            self.path_label.setText(f"{text['pathPrefix']}: {self.current_file_rel}")
        else:
            self.path_label.clear()

        if not self.page_frames:
            self.preview_placeholder.setText(text["noPreview"])

        if self.busy_chip.isVisible():
            self.busy_chip.setText(text["statusCompiling"])
            self.busy_title.setText(text["statusCompiling"])
            if self.language == "zh":
                self.busy_body.setText("正在编译论文并更新 PDF 预览")
            else:
                self.busy_body.setText("Compiling the paper and updating the PDF preview")

    def _make_button(self, accent: bool = False) -> QPushButton:
        button = QPushButton(self.overlay_bar)
        if accent:
            button.setProperty("accent", True)
        button.setCursor(Qt.PointingHandCursor)
        button.style().unpolish(button)
        button.style().polish(button)
        return button

    def _apply_shadow(
        self,
        widget: QWidget,
        blur: int = 22,
        alpha: int = 28,
        offset_x: int = 0,
        offset_y: int = 8,
    ) -> None:
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(offset_x, offset_y)
        shadow.setColor(QColor(19, 33, 54, alpha))
        widget.setGraphicsEffect(shadow)

    def toggle_files_panel(self) -> None:
        self.file_dock.setVisible(not self.file_dock.isVisible())

    def toggle_source_panel(self) -> None:
        self.editor_dock.setVisible(not self.editor_dock.isVisible())

    def toggle_log_panel(self) -> None:
        self.log_dock.setVisible(not self.log_dock.isVisible())

    def toggle_language(self) -> None:
        self.language = "zh" if self.language == "en" else "en"
        self._apply_language()

    def open_selected_file(self, index) -> None:
        path = Path(self.tree_model.filePath(index))
        if not path.is_dir():
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

        self._set_busy(True, TEXTS[self.language]["statusCompiling"])
        try:
            self._show_status(TEXTS[self.language]["statusCompiling"])
            result: CompileResult = compile_project_paper(self.project_root)
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
        finally:
            self._set_busy(False)

    def refresh_preview(self, show_message: bool = True) -> None:
        self.preview_placeholder.show()
        self.preview_placeholder.setText(TEXTS[self.language]["noPreview"])
        if not self.preview_pdf.exists():
            self._clear_preview_pages()
            if show_message:
                self._show_status(TEXTS[self.language]["statusNoPreview"])
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
            self._apply_shadow(page_frame, blur=22, alpha=24, offset_y=8)
            page_layout = QVBoxLayout(page_frame)
            page_layout.setContentsMargins(18, 14, 18, 18)
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
        viewport_width = max(420, self.preview_scroll.viewport().width() - 72)
        for pixmap, page_frame in zip(self.page_pixmaps, self.page_frames):
            page_label = page_frame._page_label  # type: ignore[attr-defined]
            scaled = pixmap.scaledToWidth(viewport_width, Qt.SmoothTransformation)
            page_label.setPixmap(scaled)
            page_label.setMinimumHeight(scaled.height())

    def _position_overlay_bar(self) -> None:
        margin = 12
        max_width = max(420, self.centralWidget().width() - margin * 2)
        desired = min(max_width, self.overlay_bar.sizeHint().width())
        height = self.overlay_bar.sizeHint().height()
        x = max(margin, (self.centralWidget().width() - desired) // 2)
        self.overlay_bar.setGeometry(x, margin, desired, height)
        self.overlay_bar.raise_()

    def _position_busy_overlay(self) -> None:
        viewport = self.preview_scroll.viewport()
        self.preview_busy_overlay.setGeometry(viewport.rect())
        self.preview_busy_overlay.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._position_overlay_bar()
        self._position_busy_overlay()
        self._rescale_preview_pages()

    def _reset_header_status(self) -> None:
        text = TEXTS[self.language]
        self.meta_label.setText(f"{self.project_root.name} · {text['statusPreview']} · {text['statusReady']}")

    def _show_status(self, message: str) -> None:
        self.meta_label.setText(f"{self.project_root.name} · {message}")
        self.status_bar.showMessage(message, 3200)
        self.status_timer.start(3200)

    def _show_error(self, title: str, message: str) -> None:
        self.meta_label.setText(f"{self.project_root.name} · {title}")
        self.status_timer.start(4000)
        QMessageBox.critical(self, title, message)

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self.compile_button.setEnabled(not busy)
        self.open_formal_button.setEnabled(not busy)
        self.files_button.setEnabled(not busy)
        if busy:
            status_text = message or TEXTS[self.language]["statusCompiling"]
            self.busy_chip.setText(status_text)
            self.busy_chip.show()
            self.busy_title.setText(status_text)
            if self.language == "zh":
                self.busy_body.setText("正在编译论文并更新 PDF 预览")
            else:
                self.busy_body.setText("Compiling the paper and updating the PDF preview")
            self._position_busy_overlay()
            self.preview_busy_overlay.show()
            self.preview_busy_overlay.raise_()
            QApplication.processEvents()
        else:
            self.busy_chip.hide()
            self.preview_busy_overlay.hide()


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
