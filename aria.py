"""
ARIA — Entry Point
Launches system tray + main window
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.makedirs(os.path.expanduser("~/.aria"), exist_ok=True)

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QColor, QFont, QBrush, QPen
from PyQt6.QtCore    import Qt, QSize

from aria_window import ARIAWindow
from aria_config import config


def make_tray_icon(size=64) -> QIcon:
    """Programmatically draw the ARIA tray icon."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Blue circle background
    p.setBrush(QBrush(QColor("#3B6FD4")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(4, 4, size-8, size-8, 12, 12)

    # White "A" letter
    p.setPen(QPen(QColor("white")))
    font = QFont("Arial", int(size * 0.38), QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "A")

    p.end()
    return QIcon(px)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ARIA")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)  # Stay alive when window is closed

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "ARIA", "System tray is not available on this system.")
        sys.exit(1)

    # ── Main window ──────────────────────────────────────────────────────
    window = ARIAWindow()
    if not config.get("start_minimized", True):
        window.show()

    # ── System tray ──────────────────────────────────────────────────────
    tray_icon = make_tray_icon(64)

    tray = QSystemTrayIcon(tray_icon, parent=app)
    tray.setToolTip("ARIA — Autonomous Resident Intelligence Assistant")

    menu = QMenu()
    menu.setStyleSheet("""
        QMenu {
            background: #FFFFFF;
            border: 1px solid #DDE3F5;
            border-radius: 10px;
            padding: 6px;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: #1E293B;
        }
        QMenu::item {
            padding: 7px 20px;
            border-radius: 6px;
        }
        QMenu::item:selected {
            background: #EEF3FF;
            color: #3B6FD4;
        }
        QMenu::separator {
            height: 1px;
            background: #DDE3F5;
            margin: 4px 8px;
        }
    """)

    def toggle_window():
        if window.isVisible():
            window.hide()
        else:
            window.show()
            window.raise_()
            window.activateWindow()

    action_show    = menu.addAction("◈  Show / Hide ARIA")
    menu.addSeparator()
    action_index   = menu.addAction("⚡  Index Files Now")
    action_system  = menu.addAction("💻  System Status")
    action_security= menu.addAction("🔐  Security Scan")
    menu.addSeparator()
    action_settings= menu.addAction("⚙  Settings")
    menu.addSeparator()
    action_quit    = menu.addAction("✕  Quit ARIA")

    action_show.triggered.connect(toggle_window)
    action_index.triggered.connect(lambda: (window.show(), window._start_index()))
    action_system.triggered.connect(lambda: (window.show(), window._on_message("how is my system")))
    action_security.triggered.connect(lambda: (window.show(), window._on_message("run security scan")))
    action_settings.triggered.connect(lambda: (window.show(), window._open_settings()))
    action_quit.triggered.connect(app.quit)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: toggle_window()
                           if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
    tray.show()

    # Show startup notification
    tray.showMessage(
        "ARIA is running",
        "Click the tray icon or press Ctrl+Space to open ARIA.",
        QSystemTrayIcon.MessageIcon.Information,
        3000,
    )

    if not config.get("start_minimized", True):
        window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
