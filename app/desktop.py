from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PyQt5.QtCore import QDir, Qt, QSize, QUrl
    from PyQt5.QtGui import QColor, QDesktopServices, QFont, QImage, QPixmap
    from PyQt5.QtWidgets import (
        QApplication,
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
        QSplitter,
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
        "title": "Vibe Paper",
        "subtitle": "Local-first paper workspace",
        "projectPrefix": "Project",
        "files": "Files",
        "source": "Source",
        "log": "Log",
        "generate": "Generate Context",
        "save": "Save File",
        "compile": "Compile Paper",
        "refresh": "Refresh Preview",
        "openFormal": "Open Formal PDF",
        "previewTitle": "PDF Preview",
        "previewSubtitle": "",
        "sourceTitle": "LaTeX Source",
        "sourceSubtitle": "",
        "logTitle": "Build Log",
        "logSubtitle": "",
        "pathPrefix": "Current file",
        "noPreview": "No preview PDF is available yet. Compile the paper or refresh after LaTeX changes.",
        "contextDone": "Project snapshot regenerated.",
        "fileSaved": "File saved.",
        "compileDone": "Paper compiled successfully.",
        "compileFailed": "Paper compilation failed. Open the build log and inspect the message.",
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
        "windowTitle": "Vibe Paper",
        "title": "Vibe Paper",
        "subtitle": "本地优先论文工作台",
        "projectPrefix": "当前项目",
        "files": "目录",
        "source": "源码",
        "log": "日志",
        "generate": "生成上下文",
        "save": "保存文件",
        "compile": "编译论文",
        "refresh": "刷新预览",
        "openFormal": "打开正式 PDF",
        "previewTitle": "PDF 预览",
        "previewSubtitle": "",
        "sourceTitle": "LaTeX 源码",
        "sourceSubtitle": "",
        "logTitle": "编译日志",
        "logSubtitle": "",
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
        "statusReady": "已就绪。",
    },
}


APP_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(232, 238, 248, 255),
        stop:0.55 rgba(239, 243, 250, 255),
        stop:1 rgba(231, 238, 246, 255));
}
QFrame#TopBar,
QFrame#PanelCard,
QFrame#PreviewPanel,
QFrame#LogPanel,
QFrame#PageCard {
    background: rgba(255, 255, 255, 166);
    border: 1px solid rgba(255, 255, 255, 150);
    border-radius: 20px;
}
QFrame#TopBar {
    border-radius: 24px;
}
QLabel#AppTitle {
    color: #1a2433;
    font-size: 30px;
    font-weight: 700;
}
QLabel#AppSubtitle,
QLabel#PanelSubtitle,
QLabel#ProjectChip,
QLabel#PathLabel {
    color: rgba(50, 66, 87, 185);
    font-size: 12px;
}
QLabel#ProjectChip {
    padding: 7px 12px;
    border-radius: 14px;
    background: rgba(240, 245, 255, 155);
    border: 1px solid rgba(255, 255, 255, 170);
}
QLabel#PanelTitle {
    color: #1d2736;
    font-size: 14px;
    font-weight: 600;
}
QPushButton {
    min-height: 38px;
    padding: 0 16px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 175);
    background: rgba(255, 255, 255, 148);
    color: #243145;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 182);
    border-color: rgba(255, 255, 255, 205);
}
QPushButton:pressed {
    background: rgba(226, 235, 250, 188);
}
QPushButton[accent="true"] {
    background: rgba(63, 110, 232, 225);
    color: #ffffff;
    border: 1px solid rgba(63, 110, 232, 240);
}
QPushButton[accent="true"]:hover {
    background: rgba(49, 94, 210, 236);
    border-color: rgba(49, 94, 210, 246);
}
QPushButton[toggleButton="true"] {
    background: rgba(255, 255, 255, 128);
}
QPushButton[toggleButton="true"]:checked {
    background: rgba(232, 240, 255, 182);
    border-color: rgba(170, 194, 244, 220);
    color: #244aa5;
}
QTreeView,
QPlainTextEdit {
    background: rgba(255, 255, 255, 106);
    border: 1px solid rgba(255, 255, 255, 150);
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
    background: #f0f5fd;
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
    color: #5a6a81;
}
QSplitter::handle {
    background: transparent;
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
        self.page_cards: list[QFrame] = []

        self._build_ui()
        self._bind_actions()
        self._load_project_tree()
        self._load_default_file()
        self._apply_language()
        self._apply_panel_visibility()
        self.refresh_preview(show_message=False)

    def _build_ui(self) -> None:
        self.setMinimumSize(QSize(1180, 780))
        self.resize(1460, 940)
        self.setStyleSheet(APP_STYLESHEET)

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(18, 18, 18, 10)
        root_layout.setSpacing(14)

        top_bar = QFrame(central)
        top_bar.setObjectName("TopBar")
        self._apply_shadow(top_bar, blur=28, alpha=60)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 16, 20, 16)
        top_layout.setSpacing(14)

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        self.title_label = QLabel(top_bar)
        self.title_label.setObjectName("AppTitle")
        self.subtitle_label = QLabel(top_bar)
        self.subtitle_label.setObjectName("AppSubtitle")
        self.project_chip = QLabel(top_bar)
        self.project_chip.setObjectName("ProjectChip")
        title_column.addWidget(self.title_label)
        title_column.addWidget(self.subtitle_label)
        title_column.addWidget(self.project_chip)
        top_layout.addLayout(title_column, stretch=1)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        self.generate_button = self._make_button()
        self.save_button = self._make_button()
        self.compile_button = self._make_button(accent=True)
        self.refresh_button = self._make_button()
        self.open_formal_button = self._make_button()
        self.files_button = self._make_button(toggle=True)
        self.source_button = self._make_button(toggle=True)
        self.log_button = self._make_button(toggle=True)
        self.lang_button = self._make_button()
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
            button_row.addWidget(button)
        top_layout.addLayout(button_row)

        self.body_splitter = QSplitter(Qt.Vertical, central)
        self.body_splitter.setChildrenCollapsible(False)

        self.main_splitter = QSplitter(Qt.Horizontal, self.body_splitter)
        self.main_splitter.setChildrenCollapsible(False)

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
        self.file_tree.setMinimumWidth(250)
        self.files_panel = self._wrap_panel(self.file_tree)
        self._apply_shadow(self.files_panel, blur=24, alpha=40)

        source_body = QWidget(self)
        source_layout = QVBoxLayout(source_body)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(8)
        self.path_label = QLabel(source_body)
        self.path_label.setObjectName("PathLabel")
        self.editor = QPlainTextEdit(source_body)
        source_layout.addWidget(self.path_label)
        source_layout.addWidget(self.editor, stretch=1)
        self.source_panel = self._wrap_panel(source_body)
        self._apply_shadow(self.source_panel, blur=24, alpha=40)

        preview_panel = QFrame(self)
        preview_panel.setObjectName("PreviewPanel")
        self._apply_shadow(preview_panel, blur=26, alpha=45)
        preview_panel_layout = QVBoxLayout(preview_panel)
        preview_panel_layout.setContentsMargins(16, 14, 16, 16)
        preview_panel_layout.setSpacing(8)
        self.preview_title = QLabel(preview_panel)
        self.preview_title.setObjectName("PanelTitle")
        self.preview_subtitle = QLabel(preview_panel)
        self.preview_subtitle.setObjectName("PanelSubtitle")
        preview_panel_layout.addWidget(self.preview_title)
        preview_panel_layout.addWidget(self.preview_subtitle)

        self.preview_scroll = QScrollArea(preview_panel)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.preview_container = QWidget(self.preview_scroll)
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(8, 10, 8, 10)
        self.preview_layout.setSpacing(18)
        self.preview_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.preview_placeholder = QLabel(self.preview_container)
        self.preview_placeholder.setAlignment(Qt.AlignCenter)
        self.preview_placeholder.setWordWrap(True)
        self.preview_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        placeholder_font = QFont()
        placeholder_font.setPointSize(13)
        self.preview_placeholder.setFont(placeholder_font)
        self.preview_layout.addWidget(self.preview_placeholder)

        self.preview_scroll.setWidget(self.preview_container)
        preview_panel_layout.addWidget(self.preview_scroll, stretch=1)
        self.preview_panel = preview_panel

        self.main_splitter.addWidget(self.files_panel)
        self.main_splitter.addWidget(self.source_panel)
        self.main_splitter.addWidget(self.preview_panel)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setStretchFactor(2, 1)

        log_panel = QFrame(self)
        log_panel.setObjectName("LogPanel")
        self._apply_shadow(log_panel, blur=24, alpha=40)
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(16, 16, 16, 16)
        log_layout.setSpacing(8)
        self.log_title = QLabel(log_panel)
        self.log_title.setObjectName("PanelTitle")
        self.log_subtitle = QLabel(log_panel)
        self.log_subtitle.setObjectName("PanelSubtitle")
        self.log_view = QPlainTextEdit(log_panel)
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(3000)
        log_layout.addWidget(self.log_title)
        log_layout.addWidget(self.log_subtitle)
        log_layout.addWidget(self.log_view, stretch=1)
        self.log_panel = log_panel

        self.body_splitter.addWidget(self.main_splitter)
        self.body_splitter.addWidget(self.log_panel)
        self.body_splitter.setStretchFactor(0, 1)
        self.body_splitter.setStretchFactor(1, 0)

        root_layout.addWidget(top_bar)
        root_layout.addWidget(self.body_splitter, stretch=1)

        self.setCentralWidget(central)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.files_button.setChecked(False)
        self.source_button.setChecked(False)
        self.log_button.setChecked(False)

    def _make_button(self, accent: bool = False, toggle: bool = False) -> QPushButton:
        button = QPushButton(self)
        if accent:
            button.setProperty("accent", True)
        if toggle:
            button.setCheckable(True)
            button.setProperty("toggleButton", True)
        return button

    def _wrap_panel(self, body: QWidget) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("PanelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        return_title = QLabel(panel)
        return_subtitle = QLabel(panel)
        return_title.setObjectName("PanelTitle")
        return_subtitle.setObjectName("PanelSubtitle")
        layout.addWidget(return_title)
        layout.addWidget(return_subtitle)
        layout.addWidget(body, stretch=1)
        panel._panel_title = return_title  # type: ignore[attr-defined]
        panel._panel_subtitle = return_subtitle  # type: ignore[attr-defined]
        return panel

    def _apply_shadow(self, widget: QWidget, blur: int = 24, alpha: int = 46) -> None:
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(120, 139, 166, alpha))
        widget.setGraphicsEffect(shadow)

    def _bind_actions(self) -> None:
        self.generate_button.clicked.connect(self.generate_context)
        self.save_button.clicked.connect(self.save_current_file)
        self.compile_button.clicked.connect(self.compile_paper)
        self.refresh_button.clicked.connect(self.refresh_preview)
        self.open_formal_button.clicked.connect(self.open_formal_pdf)
        self.files_button.toggled.connect(self._apply_panel_visibility)
        self.source_button.toggled.connect(self._apply_panel_visibility)
        self.log_button.toggled.connect(self._apply_panel_visibility)
        self.lang_button.clicked.connect(self.toggle_language)
        self.file_tree.doubleClicked.connect(self.open_selected_file)

    def _load_project_tree(self) -> None:
        self.tree_model.setRootPath(str(self.project_root))
        self.file_tree.setRootIndex(self.tree_model.index(str(self.project_root)))
        if self.paper_dir.exists():
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
        self.path_label.clear()
        self.editor.clear()

    def _apply_language(self) -> None:
        text = TEXTS[self.language]
        self.setWindowTitle(f"{text['windowTitle']} - {self.project_root.name}")
        self.title_label.setText(text["title"])
        self.subtitle_label.setText(text["subtitle"])
        self.project_chip.setText(f"{text['projectPrefix']}: {self.project_root.name}")
        self.generate_button.setText(text["generate"])
        self.save_button.setText(text["save"])
        self.compile_button.setText(text["compile"])
        self.refresh_button.setText(text["refresh"])
        self.open_formal_button.setText(text["openFormal"])
        self.files_button.setText(text["files"])
        self.source_button.setText(text["source"])
        self.log_button.setText(text["log"])
        self.lang_button.setText(text["lang"])
        self.preview_title.setText(text["previewTitle"])
        self.preview_subtitle.setText(text["previewSubtitle"])
        self.files_panel._panel_title.setText(text["files"])  # type: ignore[attr-defined]
        self.files_panel._panel_subtitle.setText(text["sourceSubtitle"])  # type: ignore[attr-defined]
        self.source_panel._panel_title.setText(text["sourceTitle"])  # type: ignore[attr-defined]
        self.source_panel._panel_subtitle.setText(text["sourceSubtitle"])  # type: ignore[attr-defined]
        self.log_title.setText(text["logTitle"])
        self.log_subtitle.setText(text["logSubtitle"])
        if self.current_file_rel:
            self.path_label.setText(f"{text['pathPrefix']}: {self.current_file_rel}")
        else:
            self.path_label.setText(text["sourceSubtitle"])
        if not self.page_pixmaps:
            self.preview_placeholder.setText(text["noPreview"])
        self.preview_subtitle.setVisible(bool(text["previewSubtitle"]))
        self.files_panel._panel_subtitle.setVisible(bool(text["sourceSubtitle"]))  # type: ignore[attr-defined]
        self.source_panel._panel_subtitle.setVisible(bool(text["sourceSubtitle"]))  # type: ignore[attr-defined]
        self.log_subtitle.setVisible(bool(text["logSubtitle"]))
        self.status_bar.showMessage(text["statusReady"], 2500)

    def _apply_panel_visibility(self) -> None:
        files_visible = self.files_button.isChecked()
        source_visible = self.source_button.isChecked()
        log_visible = self.log_button.isChecked()

        self.files_panel.setVisible(files_visible)
        self.source_panel.setVisible(source_visible)
        self.log_panel.setVisible(log_visible)

        available_width = max(960, self.width() - 80)
        files_width = 280 if files_visible else 0
        source_width = 460 if source_visible else 0
        preview_width = max(760, available_width - files_width - source_width)
        self.main_splitter.setSizes([files_width, source_width, preview_width])

        available_height = max(680, self.height() - 150)
        log_height = 220 if log_visible else 0
        main_height = max(520, available_height - log_height)
        self.body_splitter.setSizes([main_height, log_height])

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
            self.source_button.setChecked(True)
            self._apply_panel_visibility()

    def save_current_file(self) -> bool:
        if not self.current_file:
            self._show_status(TEXTS[self.language]["sourceSubtitle"])
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
            self.load_file(snapshot, show_panel=self.source_button.isChecked())
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
            self.log_button.setChecked(True)
            self._apply_panel_visibility()
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
            page_card = QFrame(self.preview_container)
            page_card.setObjectName("PageCard")
            self._apply_shadow(page_card, blur=18, alpha=32)
            page_layout = QVBoxLayout(page_card)
            page_layout.setContentsMargins(14, 14, 14, 14)
            page_layout.setSpacing(8)

            page_hint = QLabel(f"Page {page_number}", page_card)
            page_hint.setObjectName("PanelSubtitle")
            page_hint.setAlignment(Qt.AlignCenter)
            page_label = QLabel(page_card)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            page_layout.addWidget(page_hint)
            page_layout.addWidget(page_label)
            self.preview_layout.addWidget(page_card)

            page_card._page_label = page_label  # type: ignore[attr-defined]
            self.page_cards.append(page_card)
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
        for page_card in self.page_cards:
            self.preview_layout.removeWidget(page_card)
            page_card.deleteLater()
        self.page_cards = []
        self.page_pixmaps = []

    def _rescale_preview_pages(self) -> None:
        if not self.page_pixmaps or not self.page_cards:
            return
        viewport_width = max(360, self.preview_scroll.viewport().width() - 96)
        for pixmap, page_card in zip(self.page_pixmaps, self.page_cards):
            page_label = page_card._page_label  # type: ignore[attr-defined]
            scaled = pixmap.scaledToWidth(viewport_width, Qt.SmoothTransformation)
            page_label.setPixmap(scaled)
            page_label.setMinimumHeight(scaled.height())

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._apply_panel_visibility()
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
