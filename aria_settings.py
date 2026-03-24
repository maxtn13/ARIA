"""
ARIA Settings Dialog — tabbed settings with live save
"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QComboBox, QListWidget, QListWidgetItem,
    QFileDialog, QTabWidget, QWidget, QSpinBox, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from aria_config import config


C = {
    "bg":     "#F4F7FF", "bg2": "#FFFFFF", "bg3": "#EDF1FB",
    "border": "#DDE3F5", "blue": "#3B6FD4", "blue_l": "#EEF3FF",
    "text":   "#1E293B", "text2": "#475569", "muted": "#94A3B8",
    "green": "#059669",  "red": "#DC2626",
}

BASE_STYLE = f"""
    QDialog {{
        background:{C['bg']};
        border:1px solid {C['border']};
        border-radius:12px;
    }}
    QWidget {{
        font-family:'Segoe UI','SF Pro Text',Arial,sans-serif;
        font-size:13px;
        color:{C['text']};
    }}
    QTabWidget::pane {{
        background:{C['bg2']};
        border:1px solid {C['border']};
        border-radius:8px;
    }}
    QTabBar::tab {{
        background:{C['bg3']};
        color:{C['text2']};
        border:1px solid {C['border']};
        border-radius:6px;
        padding:6px 16px;
        margin:2px;
        font-size:12px;
        font-weight:500;
    }}
    QTabBar::tab:selected {{
        background:{C['blue']};
        color:white;
        border-color:{C['blue']};
    }}
    QLineEdit, QComboBox, QSpinBox {{
        background:{C['bg2']};
        border:1.5px solid {C['border']};
        border-radius:8px;
        padding:6px 10px;
        font-size:13px;
        color:{C['text']};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border-color:{C['blue']};
    }}
    QCheckBox {{
        spacing:8px;
        font-size:13px;
    }}
    QCheckBox::indicator {{
        width:18px; height:18px;
        border:1.5px solid {C['border']};
        border-radius:5px;
        background:{C['bg2']};
    }}
    QCheckBox::indicator:checked {{
        background:{C['blue']};
        border-color:{C['blue']};
        image: none;
    }}
    QListWidget {{
        background:{C['bg2']};
        border:1.5px solid {C['border']};
        border-radius:8px;
        padding:4px;
    }}
    QListWidget::item {{
        padding:6px 8px;
        border-radius:5px;
    }}
    QListWidget::item:selected {{
        background:{C['blue_l']};
        color:{C['blue']};
    }}
    QScrollBar:vertical {{
        background:transparent; width:5px;
    }}
    QScrollBar::handle:vertical {{
        background:{C['border']}; border-radius:2px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
"""


def section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"font-size:9px; font-weight:700; color:{C['muted']}; letter-spacing:1.5px; padding:4px 0;")
    return lbl


def btn(text, primary=False) -> QPushButton:
    b = QPushButton(text)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if primary:
        b.setStyleSheet(f"""
            QPushButton {{
                background:{C['blue']}; color:white;
                border:none; border-radius:8px;
                padding:7px 18px; font-size:13px; font-weight:600;
            }}
            QPushButton:hover {{ background:#2A57B5; }}
        """)
    else:
        b.setStyleSheet(f"""
            QPushButton {{
                background:{C['bg3']}; color:{C['text2']};
                border:1px solid {C['border']}; border-radius:8px;
                padding:7px 16px; font-size:13px;
            }}
            QPushButton:hover {{
                background:{C['blue_l']}; color:{C['blue']};
                border-color:{C['blue']};
            }}
        """)
    return b


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ARIA Settings")
        self.setMinimumSize(520, 460)
        self.setStyleSheet(BASE_STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(50)
        hdr.setStyleSheet(f"background:{C['bg2']}; border-bottom:1px solid {C['border']}; border-radius:12px 12px 0 0;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(16,0,12,0)
        title = QLabel("⚙ Settings")
        title.setStyleSheet(f"font-size:15px; font-weight:700; color:{C['text']};")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26,26)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background:{C['bg3']}; color:{C['muted']};
                border:1px solid {C['border']}; border-radius:13px;
                font-size:12px; font-weight:700;
            }}
            QPushButton:hover {{ background:{C['red']}; color:white; border-color:{C['red']}; }}
        """)
        close_btn.clicked.connect(self.accept)
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(close_btn)
        outer.addWidget(hdr)

        # Tabs
        body = QWidget()
        body.setStyleSheet(f"background:{C['bg']}; padding:12px;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(12,12,12,12)

        tabs = QTabWidget()
        tabs.addTab(self._tab_general(),  "General")
        tabs.addTab(self._tab_indexing(), "Indexing")
        tabs.addTab(self._tab_llm(),      "LLM / AI")
        tabs.addTab(self._tab_about(),    "About")
        bl.addWidget(tabs)

        # Footer
        footer = QHBoxLayout()
        footer.setSpacing(8)
        footer.addStretch()
        save_btn = btn("Save Settings", primary=True)
        save_btn.clicked.connect(self._save)
        cancel_btn = btn("Cancel")
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)
        footer.addWidget(save_btn)
        bl.addLayout(footer)

        outer.addWidget(body, 1)

    # ── GENERAL TAB ───────────────────────────────────────────────────────
    def _tab_general(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(10)

        l.addWidget(section_label("Startup"))
        self.chk_tray = QCheckBox("Start minimized to system tray")
        self.chk_tray.setChecked(config.get("start_minimized", True))
        l.addWidget(self.chk_tray)

        self.chk_auto_idx = QCheckBox("Auto-index files on startup (if index is empty)")
        self.chk_auto_idx.setChecked(config.get("auto_index_on_start", False))
        l.addWidget(self.chk_auto_idx)

        l.addWidget(section_label("Search"))
        lim_row = QHBoxLayout()
        lim_row.addWidget(QLabel("Max search results:"))
        self.spin_results = QSpinBox()
        self.spin_results.setRange(5, 50)
        self.spin_results.setValue(config.get("max_results", 12))
        self.spin_results.setFixedWidth(80)
        lim_row.addWidget(self.spin_results)
        lim_row.addStretch()
        l.addLayout(lim_row)

        self.chk_semantic = QCheckBox("Enable semantic search (requires sentence-transformers, ~500MB)")
        self.chk_semantic.setChecked(config.get("semantic_search", False))
        l.addWidget(self.chk_semantic)

        l.addStretch()
        return w

    # ── INDEXING TAB ──────────────────────────────────────────────────────
    def _tab_indexing(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(10)

        l.addWidget(section_label("Indexed Directories"))

        self.paths_list = QListWidget()
        self.paths_list.setFixedHeight(120)
        for p in config.get("index_paths", []):
            self.paths_list.addItem(p)
        l.addWidget(self.paths_list)

        path_btns = QHBoxLayout()
        path_btns.setSpacing(6)
        add_btn = btn("+ Add Path")
        add_btn.clicked.connect(self._add_path)
        rem_btn = btn("− Remove")
        rem_btn.clicked.connect(self._rem_path)
        path_btns.addWidget(add_btn)
        path_btns.addWidget(rem_btn)
        path_btns.addStretch()
        l.addLayout(path_btns)

        info = QLabel("ℹ ARIA will index all files in these directories (skipping hidden folders).")
        info.setStyleSheet(f"font-size:11px; color:{C['muted']}; font-style:italic;")
        info.setWordWrap(True)
        l.addWidget(info)

        l.addWidget(section_label("Database"))
        db_row = QHBoxLayout()
        db_lbl = QLabel("Index DB path:")
        self.db_path_edit = QLineEdit(config.get("index_db_path", ""))
        db_browse = btn("Browse")
        db_browse.clicked.connect(self._browse_db)
        db_row.addWidget(db_lbl)
        db_row.addWidget(self.db_path_edit)
        db_row.addWidget(db_browse)
        l.addLayout(db_row)

        reset_btn = btn("🗑 Clear Index Database")
        reset_btn.clicked.connect(self._clear_db)
        l.addWidget(reset_btn)

        l.addStretch()
        return w

    # ── LLM TAB ──────────────────────────────────────────────────────────
    def _tab_llm(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(10)

        info = QLabel(
            "ARIA works without a local LLM using its built-in intent engine.\n"
            "For richer AI conversations, install Ollama and pull a model."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size:12px; color:{C['text2']}; background:{C['blue_l']}; "
                           f"border:1px solid {C['border']}; border-radius:8px; padding:10px;")
        l.addWidget(info)

        l.addWidget(section_label("Ollama Settings"))

        url_row = QHBoxLayout()
        url_row.addWidget(QLabel("Ollama URL:"))
        self.ollama_url = QLineEdit(config.get("ollama_url", "http://localhost:11434"))
        url_row.addWidget(self.ollama_url)
        l.addLayout(url_row)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self.ollama_model = QComboBox()
        self.ollama_model.addItems(["mistral","llama3","phi3","gemma","codellama","llama3.2:1b"])
        self.ollama_model.setCurrentText(config.get("ollama_model", "mistral"))
        self.ollama_model.setEditable(True)
        model_row.addWidget(self.ollama_model)
        l.addLayout(model_row)

        self.chk_ollama = QCheckBox("Use Ollama for AI chat (when available)")
        self.chk_ollama.setChecked(config.get("use_ollama", True))
        l.addWidget(self.chk_ollama)

        test_btn = btn("Test Ollama Connection")
        test_btn.clicked.connect(self._test_ollama)
        l.addWidget(test_btn)
        self.ollama_status = QLabel("")
        l.addWidget(self.ollama_status)

        l.addStretch()

        install = QLabel("Install Ollama: https://ollama.com  •  Then run: ollama pull mistral")
        install.setStyleSheet(f"font-size:11px; color:{C['muted']};")
        l.addWidget(install)
        return w

    # ── ABOUT TAB ────────────────────────────────────────────────────────
    def _tab_about(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setSpacing(14)

        logo = QLabel("◈")
        logo.setStyleSheet(f"font-size:48px; color:{C['blue']};")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name = QLabel("ARIA v1.0.0")
        name.setStyleSheet(f"font-size:18px; font-weight:700; color:{C['text']};")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Autonomous Resident Intelligence Assistant")
        sub.setStyleSheet(f"font-size:13px; color:{C['muted']};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc = QLabel(
            "Fully local · Fully private · Open Source\n"
            "Find files · Monitor your system · Detect threats\n\n"
            "Built with Python, PyQt6, and SQLite\n"
            "Your data never leaves your machine."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"font-size:12px; color:{C['text2']}; line-height:1.7;")

        badge = QLabel("MIT License — Free & Open Source")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"font-size:11px; color:{C['muted']};")

        for widget in [logo, name, sub, desc, badge]:
            l.addWidget(widget)
        l.addStretch()
        return w

    # ── ACTIONS ──────────────────────────────────────────────────────────
    def _add_path(self):
        path = QFileDialog.getExistingDirectory(self, "Choose Directory")
        if path:
            items = [self.paths_list.item(i).text() for i in range(self.paths_list.count())]
            if path not in items:
                self.paths_list.addItem(path)

    def _rem_path(self):
        for item in self.paths_list.selectedItems():
            self.paths_list.takeItem(self.paths_list.row(item))

    def _browse_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Choose DB location", "", "SQLite DB (*.db)")
        if path:
            self.db_path_edit.setText(path)

    def _clear_db(self):
        reply = QMessageBox.question(self, "Clear Index",
            "This will delete all indexed files. ARIA will not be able to search until you re-index. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db = config.get("index_db_path")
            if os.path.exists(db):
                os.remove(db)
                QMessageBox.information(self, "Done", "Index cleared. Re-index to search files.")

    def _test_ollama(self):
        try:
            import urllib.request
            url = self.ollama_url.text() + "/api/tags"
            urllib.request.urlopen(url, timeout=3)
            self.ollama_status.setText("✅ Connected to Ollama!")
            self.ollama_status.setStyleSheet(f"color:{C['green']}; font-size:12px;")
        except Exception as e:
            self.ollama_status.setText(f"❌ Cannot connect: {e}")
            self.ollama_status.setStyleSheet(f"color:{C['red']}; font-size:12px;")

    def _save(self):
        config.update({
            "start_minimized":    self.chk_tray.isChecked(),
            "auto_index_on_start":self.chk_auto_idx.isChecked(),
            "max_results":        self.spin_results.value(),
            "semantic_search":    self.chk_semantic.isChecked(),
            "index_paths":        [self.paths_list.item(i).text() for i in range(self.paths_list.count())],
            "index_db_path":      self.db_path_edit.text(),
            "ollama_url":         self.ollama_url.text(),
            "ollama_model":       self.ollama_model.currentText(),
            "use_ollama":         self.chk_ollama.isChecked(),
        })
        self.accept()
