# """
# ARIA Main Window — bright, clean, modern PyQt6 UI
# """
# import sys, os, re
# sys.path.insert(0, os.path.dirname(__file__))

# from PyQt6.QtWidgets import (
#     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
#     QLabel, QPushButton, QLineEdit, QTextEdit, QScrollArea,
#     QFrame, QProgressBar, QStackedWidget, QApplication, QSizeGrip,
# )
# from PyQt6.QtCore  import Qt, QTimer, pyqtSignal, QPoint, QSize, QThread
# from PyQt6.QtGui   import (QFont, QColor, QPalette, QIcon, QPixmap,
#                             QPainter, QBrush, QPen, QLinearGradient,
#                             QTextCursor, QKeySequence, QShortcut)

# from aria_config  import config
# from aria_workers import IndexWorker, ChatWorker, StatsWorker


# # ─── COLOUR PALETTE ──────────────────────────────────────────────────────────
# C = {
#     "bg":        "#F4F7FF",
#     "bg2":       "#FFFFFF",
#     "bg3":       "#EDF1FB",
#     "sidebar":   "#FFFFFF",
#     "border":    "#DDE3F5",
#     "blue":      "#3B6FD4",
#     "blue_l":    "#EEF3FF",
#     "blue_d":    "#2A57B5",
#     "purple":    "#7C3AED",
#     "green":     "#059669",
#     "green_l":   "#ECFDF5",
#     "amber":     "#D97706",
#     "amber_l":   "#FFFBEB",
#     "red":       "#DC2626",
#     "red_l":     "#FEF2F2",
#     "text":      "#1E293B",
#     "text2":     "#475569",
#     "muted":     "#94A3B8",
#     "user_bg":   "#3B6FD4",
#     "user_text": "#FFFFFF",
#     "aria_bg":   "#FFFFFF",
#     "aria_text": "#1E293B",
# }

# STYLESHEET = f"""
# QMainWindow, QWidget#central {{
#     background: {C['bg']};
# }}
# QWidget {{
#     font-family: 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif;
#     font-size: 13px;
#     color: {C['text']};
# }}
# QScrollBar:vertical {{
#     background: transparent;
#     width: 6px;
#     margin: 0;
# }}
# QScrollBar::handle:vertical {{
#     background: {C['border']};
#     border-radius: 3px;
#     min-height: 30px;
# }}
# QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
# QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
# QScrollArea {{ border: none; background: transparent; }}
# QScrollArea > QWidget > QWidget {{ background: transparent; }}
# QToolTip {{
#     background: {C['text']};
#     color: white;
#     border: none;
#     padding: 4px 8px;
#     border-radius: 4px;
#     font-size: 11px;
# }}
# """


# def make_icon_label(emoji: str, size=32, bg=None, radius=8) -> QLabel:
#     lbl = QLabel(emoji)
#     lbl.setFixedSize(size, size)
#     lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
#     bg_c = bg or C['blue_l']
#     lbl.setStyleSheet(f"""
#         background:{bg_c}; border-radius:{radius}px;
#         font-size:{size//2}px; padding:0;
#     """)
#     return lbl


# def card(parent=None, bg=C['bg2'], border=C['border'], radius=12, padding="12px 14px") -> QFrame:
#     f = QFrame(parent)
#     f.setStyleSheet(f"""
#         QFrame {{
#             background:{bg};
#             border:1px solid {border};
#             border-radius:{radius}px;
#         }}
#     """)
#     lay = QVBoxLayout(f)
#     lay.setContentsMargins(*[int(x.replace('px','')) for x in padding.split()])
#     lay.setSpacing(6)
#     return f


# # ─── HEADER ──────────────────────────────────────────────────────────────────

# class Header(QWidget):
#     settings_clicked  = pyqtSignal()
#     index_clicked     = pyqtSignal()
#     minimize_clicked  = pyqtSignal()
#     close_clicked     = pyqtSignal()

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setFixedHeight(56)
#         self.setStyleSheet(f"""
#             background:{C['bg2']};
#             border-bottom:1px solid {C['border']};
#         """)
#         lay = QHBoxLayout(self)
#         lay.setContentsMargins(16, 0, 12, 0)
#         lay.setSpacing(10)

#         # Logo
#         logo_icon = QLabel("◈")
#         logo_icon.setStyleSheet(f"""
#             font-size:22px; color:{C['blue']};
#             font-weight:bold; padding:0;
#         """)
#         logo_text = QLabel("ARIA")
#         logo_text.setStyleSheet(f"""
#             font-size:16px; font-weight:700;
#             color:{C['text']}; letter-spacing:3px;
#         """)
#         sub = QLabel("Autonomous Resident Intelligence")
#         sub.setStyleSheet(f"font-size:10px; color:{C['muted']}; letter-spacing:0.5px;")

#         logo_v = QVBoxLayout()
#         logo_v.setSpacing(0)
#         logo_v.setContentsMargins(0,0,0,0)
#         logo_v.addWidget(logo_text)
#         logo_v.addWidget(sub)

#         lay.addWidget(logo_icon)
#         lay.addLayout(logo_v)
#         lay.addStretch()

#         # Status dot
#         self.status_dot = QLabel("●  OFFLINE")
#         self.status_dot.setStyleSheet(f"font-size:11px; color:{C['muted']};")

#         # Buttons
#         btn_style = f"""
#             QPushButton {{
#                 background:{C['bg3']};
#                 color:{C['text2']};
#                 border:1px solid {C['border']};
#                 border-radius:7px;
#                 padding:5px 12px;
#                 font-size:12px;
#                 font-weight:500;
#             }}
#             QPushButton:hover {{
#                 background:{C['blue_l']};
#                 color:{C['blue']};
#                 border-color:{C['blue']};
#             }}
#         """
#         btn_idx = QPushButton("⚡ Index Files")
#         btn_idx.setStyleSheet(btn_style)
#         btn_idx.setCursor(Qt.CursorShape.PointingHandCursor)
#         btn_idx.clicked.connect(self.index_clicked)

#         btn_set = QPushButton("⚙ Settings")
#         btn_set.setStyleSheet(btn_style)
#         btn_set.setCursor(Qt.CursorShape.PointingHandCursor)
#         btn_set.clicked.connect(self.settings_clicked)

#         # Window controls
#         for txt, sig, color in [
#             ("–", self.minimize_clicked, C['amber']),
#             ("✕", self.close_clicked,   C['red']),
#         ]:
#             b = QPushButton(txt)
#             b.setFixedSize(26, 26)
#             b.setStyleSheet(f"""
#                 QPushButton {{
#                     background:{C['bg3']}; color:{C['muted']};
#                     border:1px solid {C['border']}; border-radius:13px;
#                     font-size:12px; font-weight:700;
#                 }}
#                 QPushButton:hover {{
#                     background:{color}; color:white; border-color:{color};
#                 }}
#             """)
#             b.setCursor(Qt.CursorShape.PointingHandCursor)
#             b.clicked.connect(sig)
#             lay.addWidget(b)

#         lay.insertWidget(lay.count()-2, self.status_dot)
#         lay.insertWidget(lay.count()-2, btn_idx)
#         lay.insertWidget(lay.count()-2, btn_set)

#     def set_status(self, online: bool):
#         if online:
#             self.status_dot.setText("●  READY")
#             self.status_dot.setStyleSheet(f"font-size:11px; color:{C['green']};")
#         else:
#             self.status_dot.setText("●  OFFLINE")
#             self.status_dot.setStyleSheet(f"font-size:11px; color:{C['muted']};")


# # ─── SIDEBAR ─────────────────────────────────────────────────────────────────

# class SidebarButton(QPushButton):
#     def __init__(self, emoji, title, subtitle="", parent=None):
#         super().__init__(parent)
#         self.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.setFixedHeight(52)
#         lay = QHBoxLayout(self)
#         lay.setContentsMargins(8,0,8,0)
#         lay.setSpacing(10)

#         icon = QLabel(emoji)
#         icon.setFixedSize(30,30)
#         icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         icon.setStyleSheet(f"font-size:16px; background:{C['blue_l']}; border-radius:7px;")

#         txt = QVBoxLayout()
#         txt.setSpacing(1)
#         t = QLabel(title)
#         t.setStyleSheet(f"font-size:13px; font-weight:600; color:{C['text']};")
#         txt.addWidget(t)
#         if subtitle:
#             s = QLabel(subtitle)
#             s.setStyleSheet(f"font-size:11px; color:{C['muted']};")
#             txt.addWidget(s)

#         lay.addWidget(icon)
#         lay.addLayout(txt)
#         lay.addStretch()

#         self.setStyleSheet(f"""
#             QPushButton {{
#                 background:transparent;
#                 border:1px solid transparent;
#                 border-radius:10px;
#                 text-align:left;
#             }}
#             QPushButton:hover {{
#                 background:{C['blue_l']};
#                 border-color:{C['border']};
#             }}
#         """)


# class MiniStat(QWidget):
#     def __init__(self, label, color, parent=None):
#         super().__init__(parent)
#         self._color = color
#         lay = QHBoxLayout(self)
#         lay.setContentsMargins(0,2,0,2)
#         lay.setSpacing(8)

#         self._lbl = QLabel(label)
#         self._lbl.setFixedWidth(36)
#         self._lbl.setStyleSheet(f"font-size:10px; color:{C['muted']}; font-weight:600; letter-spacing:0.5px;")
#         self._lbl.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)

#         bar_bg = QFrame()
#         bar_bg.setFixedHeight(4)
#         bar_bg.setStyleSheet(f"background:{C['bg3']}; border-radius:2px;")
#         bar_lay = QHBoxLayout(bar_bg)
#         bar_lay.setContentsMargins(0,0,0,0)
#         self._bar = QFrame()
#         self._bar.setFixedHeight(4)
#         self._bar.setStyleSheet(f"background:{color}; border-radius:2px;")
#         bar_lay.addWidget(self._bar)
#         bar_lay.addStretch()
#         bar_bg.setFixedWidth(100)

#         self._val = QLabel("—")
#         self._val.setFixedWidth(38)
#         self._val.setStyleSheet(f"font-size:11px; font-weight:700; color:{C['text2']};")

#         lay.addWidget(self._lbl)
#         lay.addWidget(bar_bg)
#         lay.addWidget(self._val)
#         self._bar_bg = bar_bg

#     def update_val(self, pct: float, label: str = None):
#         w = int(max(2, min(100, pct)))
#         self._bar.setFixedWidth(w)
#         self._val.setText(label or f"{pct:.0f}%")


# class Sidebar(QWidget):
#     quick_action = pyqtSignal(str)

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setFixedWidth(220)
#         self.setStyleSheet(f"""
#             background:{C['sidebar']};
#             border-right:1px solid {C['border']};
#         """)
#         outer = QVBoxLayout(self)
#         outer.setContentsMargins(10,12,10,10)
#         outer.setSpacing(10)

#         # Quick actions
#         sec_lbl = QLabel("QUICK ACTIONS")
#         sec_lbl.setStyleSheet(f"font-size:9px; font-weight:700; color:{C['muted']}; letter-spacing:1.5px; padding-left:4px;")
#         outer.addWidget(sec_lbl)

#         actions = [
#             ("🔍", "Find File",     "By name or content",  "find file"),
#             ("💻", "System Status", "CPU · RAM · Disk",    "how is my system"),
#             ("🔐", "Security Scan", "Threats & anomalies", "run security scan"),
#             ("📦", "Duplicates",    "Free up disk space",  "find duplicate files"),
#             ("🕑", "Recent Files",  "Last modified",       "show recent files"),
#             ("❓", "Help",          "All commands",        "help"),
#         ]
#         for emoji, title, sub, cmd in actions:
#             btn = SidebarButton(emoji, title, sub)
#             btn.clicked.connect(lambda _, c=cmd: self.quick_action.emit(c))
#             outer.addWidget(btn)

#         # Divider
#         div = QFrame()
#         div.setFrameShape(QFrame.Shape.HLine)
#         div.setStyleSheet(f"color:{C['border']};")
#         outer.addWidget(div)

#         # Live stats
#         sec2 = QLabel("LIVE SYSTEM")
#         sec2.setStyleSheet(f"font-size:9px; font-weight:700; color:{C['muted']}; letter-spacing:1.5px; padding-left:4px;")
#         outer.addWidget(sec2)

#         self.cpu_stat  = MiniStat("CPU",  C['blue'])
#         self.ram_stat  = MiniStat("RAM",  C['purple'])
#         self.disk_stat = MiniStat("DISK", C['amber'])
#         outer.addWidget(self.cpu_stat)
#         outer.addWidget(self.ram_stat)
#         outer.addWidget(self.disk_stat)

#         outer.addStretch()

#         # Index stats
#         self.idx_label = QLabel("Index: not built")
#         self.idx_label.setStyleSheet(f"font-size:10px; color:{C['muted']}; padding:4px;")
#         self.idx_label.setWordWrap(True)
#         outer.addWidget(self.idx_label)

#     def update_stats(self, data: dict):
#         cpu  = data.get("cpu",{}).get("percent",0)
#         ram  = data.get("memory",{}).get("percent",0)
#         disk = (data.get("disk") or [{}])[0].get("percent",0)
#         self.cpu_stat.update_val(cpu)
#         self.ram_stat.update_val(ram)
#         self.disk_stat.update_val(disk)

#     def update_index(self, total: int):
#         self.idx_label.setText(f"Index: {total:,} files")
#         self.idx_label.setStyleSheet(f"font-size:10px; color:{C['green']}; padding:4px;")


# # ─── CHAT MESSAGE WIDGETS ────────────────────────────────────────────────────

# class MessageBubble(QFrame):
#     def __init__(self, text: str, role: str = "aria", parent=None):
#         super().__init__(parent)
#         self.setObjectName("bubble")
#         is_user = role == "user"

#         outer = QVBoxLayout(self)
#         outer.setContentsMargins(0, 0, 0, 0)
#         outer.setSpacing(4)

#         row = QHBoxLayout()
#         row.setSpacing(10)
#         if is_user:
#             row.addStretch()

#         # Avatar
#         av = QLabel("ME" if is_user else "AR")
#         av.setFixedSize(28, 28)
#         av.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         av.setStyleSheet(f"""
#             background:{"#3B6FD4" if is_user else C['bg3']};
#             color:{"white" if is_user else C['blue']};
#             border-radius:8px;
#             font-size:9px;
#             font-weight:700;
#             letter-spacing:0.5px;
#         """)

#         # Bubble
#         bbl = QLabel()
#         bbl.setWordWrap(True)
#         bbl.setTextFormat(Qt.TextFormat.RichText)
#         bbl.setText(self._md(text))
#         bbl.setMaximumWidth(520)
#         bbl.setStyleSheet(f"""
#             background:{"#3B6FD4" if is_user else C['aria_bg']};
#             color:{"white" if is_user else C['text']};
#             border:1px solid {"#3B6FD4" if is_user else C['border']};
#             border-radius:{"14px 4px 14px 14px" if is_user else "4px 14px 14px 14px"};
#             padding:10px 14px;
#             font-size:13px;
#             line-height:1.6;
#         """)

#         if is_user:
#             row.addWidget(bbl)
#             row.addWidget(av)
#         else:
#             row.addWidget(av)
#             row.addWidget(bbl)
#             row.addStretch()

#         outer.addLayout(row)

#         # Timestamp
#         from datetime import datetime
#         ts = QLabel(datetime.now().strftime("%H:%M"))
#         ts.setStyleSheet(f"font-size:10px; color:{C['muted']}; padding-left:{38 if not is_user else 0}px;")
#         if is_user:
#             ts_row = QHBoxLayout()
#             ts_row.addStretch()
#             ts_row.addWidget(ts)
#             outer.addLayout(ts_row)
#         else:
#             outer.addWidget(ts)

#     def _md(self, text: str) -> str:
#         """Convert **bold**, bullet, newline to HTML."""
#         text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
#         text = re.sub(r'`(.*?)`', r'<code style="background:#F1F5F9;padding:1px 4px;border-radius:3px;font-family:monospace;">\1</code>', text)
#         text = text.replace('\n', '<br>')
#         return text


# class FileResultCard(QFrame):
#     def __init__(self, files: list, parent=None):
#         super().__init__(parent)
#         lay = QVBoxLayout(self)
#         lay.setContentsMargins(8, 4, 8, 4)
#         lay.setSpacing(4)

#         for f in files[:10]:
#             row = QFrame()
#             row.setStyleSheet(f"""
#                 QFrame {{
#                     background:{C['bg2']};
#                     border:1px solid {C['border']};
#                     border-radius:8px;
#                 }}
#                 QFrame:hover {{
#                     border-color:{C['blue']};
#                     background:{C['blue_l']};
#                 }}
#             """)
#             rl = QHBoxLayout(row)
#             rl.setContentsMargins(10, 8, 10, 8)
#             rl.setSpacing(10)

#             # File icon
#             icon_map = {
#                 '.pdf':'📕','.doc':'📘','.docx':'📘',
#                 '.xls':'📗','.xlsx':'📗','.csv':'📊',
#                 '.py':'🐍','.js':'🟨','.ts':'🔷',
#                 '.html':'🌐','.css':'🎨','.json':'📋',
#                 '.jpg':'🖼','.jpeg':'🖼','.png':'🖼',
#                 '.mp4':'🎬','.mp3':'🎵','.zip':'📦',
#                 '.txt':'📄','.md':'📝','.sh':'⚙',
#             }
#             icon = icon_map.get(f.get('extension','').lower(),'📄')
#             ic = QLabel(icon)
#             ic.setFixedSize(28,28)
#             ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             ic.setStyleSheet("font-size:16px;")
#             rl.addWidget(ic)

#             info = QVBoxLayout()
#             info.setSpacing(2)
#             nm = QLabel(f.get('name',''))
#             nm.setStyleSheet(f"font-weight:600; font-size:13px; color:{C['text']};")
#             path_lbl = QLabel(f.get('directory',''))
#             path_lbl.setStyleSheet(f"font-size:10px; color:{C['muted']}; font-family:monospace;")
#             path_lbl.setWordWrap(False)
#             info.addWidget(nm)
#             info.addWidget(path_lbl)

#             # Tags
#             tags = f.get('tags', [])[:3]
#             if tags or f.get('size'):
#                 trow = QHBoxLayout()
#                 trow.setSpacing(4)
#                 for tg in tags:
#                     t = QLabel(tg)
#                     t.setStyleSheet(f"""
#                         background:{C['blue_l']}; color:{C['blue']};
#                         border-radius:10px; padding:1px 7px;
#                         font-size:9px; font-weight:600;
#                     """)
#                     trow.addWidget(t)
#                 if f.get('size'):
#                     sz = QLabel(f['size'])
#                     sz.setStyleSheet(f"font-size:10px; color:{C['muted']};")
#                     trow.addWidget(sz)
#                 if f.get('modified'):
#                     mod = QLabel(f['modified'])
#                     mod.setStyleSheet(f"font-size:10px; color:{C['muted']};")
#                     trow.addWidget(mod)
#                 trow.addStretch()
#                 info.addLayout(trow)

#             rl.addLayout(info)
#             rl.addStretch()
#             lay.addWidget(row)


# class SecurityCard(QFrame):
#     def __init__(self, data: dict, parent=None):
#         super().__init__(parent)
#         lay = QVBoxLayout(self)
#         lay.setContentsMargins(8, 4, 8, 4)
#         lay.setSpacing(6)

#         risk = data.get("risk_score", 0)
#         if risk == 0:   color, label = C['green'],  "ALL CLEAR"
#         elif risk < 40: color, label = C['amber'],  "LOW RISK"
#         elif risk < 70: color, label = C['amber'],  "MODERATE"
#         else:           color, label = C['red'],    "HIGH RISK"

#         score_row = QFrame()
#         score_row.setStyleSheet(f"background:{color}18; border:1px solid {color}44; border-radius:8px;")
#         sr = QHBoxLayout(score_row)
#         sr.setContentsMargins(12,8,12,8)
#         lbl = QLabel(f"Risk Score: {risk}/100")
#         lbl.setStyleSheet(f"font-weight:700; color:{color}; font-size:14px;")
#         badge = QLabel(label)
#         badge.setStyleSheet(f"background:{color}; color:white; border-radius:4px; padding:2px 8px; font-size:10px; font-weight:700;")
#         sr.addWidget(lbl)
#         sr.addStretch()
#         sr.addWidget(badge)
#         lay.addWidget(score_row)

#         # Ports
#         ports = data.get("open_ports", [])
#         if ports:
#             pl = QLabel(f"🔌 {len(ports)} listening port(s) · {sum(1 for p in ports if p['suspicious'])} suspicious")
#             pl.setStyleSheet(f"font-size:12px; color:{C['text2']};")
#             lay.addWidget(pl)

#         # Processes
#         procs = data.get("suspicious_processes", [])
#         for p in procs:
#             r = QLabel(f"⚠ Suspicious process: {p['name']} (PID {p['pid']})")
#             r.setStyleSheet(f"background:{C['red_l']}; color:{C['red']}; padding:6px 10px; border-radius:6px; font-size:12px;")
#             lay.addWidget(r)

#         # Integrity
#         for ch in data.get("integrity_changes", []):
#             r = QLabel(f"🔴 Modified: {ch['file']}")
#             r.setStyleSheet(f"background:{C['red_l']}; color:{C['red']}; padding:6px 10px; border-radius:6px; font-size:12px;")
#             lay.addWidget(r)

#         # USB
#         usb = data.get("usb_devices", [])
#         if usb:
#             r = QLabel(f"🔌 {len(usb)} USB device(s) connected")
#             r.setStyleSheet(f"background:{C['amber_l']}; color:{C['amber']}; padding:6px 10px; border-radius:6px; font-size:12px;")
#             lay.addWidget(r)


# class SystemCard(QFrame):
#     def __init__(self, data: dict, parent=None):
#         super().__init__(parent)
#         lay = QVBoxLayout(self)
#         lay.setContentsMargins(8, 4, 8, 4)
#         lay.setSpacing(6)

#         cpu  = data.get("cpu",{}).get("percent",0)
#         ram  = data.get("memory",{}).get("percent",0)
#         score = data.get("health_score",0)
#         sys = data.get("system",{})

#         sc = C['green'] if score>=80 else C['amber'] if score>=50 else C['red']
#         top = QFrame()
#         top.setStyleSheet(f"background:{sc}12; border:1px solid {sc}30; border-radius:8px;")
#         tl = QHBoxLayout(top)
#         tl.setContentsMargins(12,8,12,8)
#         hl = QLabel(f"Health: {score}/100")
#         hl.setStyleSheet(f"font-weight:700; color:{sc}; font-size:14px;")
#         sl = QLabel(f"{sys.get('os','')} · {sys.get('hostname','')} · ⏱ {sys.get('uptime','')}")
#         sl.setStyleSheet(f"font-size:11px; color:{C['muted']};")
#         tl.addWidget(hl); tl.addStretch(); tl.addWidget(sl)
#         lay.addWidget(top)

#         for label, val, color in [
#             ("CPU",  cpu,  C['blue']),
#             ("RAM",  ram,  C['purple']),
#             ((data.get("disk") or [{}])[0].get("mountpoint","Disk"),
#              (data.get("disk") or [{}])[0].get("percent",0), C['amber']),
#         ]:
#             row = QHBoxLayout()
#             lbl = QLabel(str(label))
#             lbl.setFixedWidth(45)
#             lbl.setStyleSheet(f"font-size:11px; font-weight:600; color:{C['text2']};")
#             bar_bg = QFrame()
#             bar_bg.setFixedHeight(6)
#             bar_bg.setStyleSheet(f"background:{C['bg3']}; border-radius:3px;")
#             bar = QFrame(bar_bg)
#             bar.setFixedHeight(6)
#             bar.setStyleSheet(f"background:{color}; border-radius:3px;")
#             bar.setFixedWidth(max(4, int(val * 1.5)))
#             val_lbl = QLabel(f"{val:.0f}%")
#             val_lbl.setFixedWidth(38)
#             val_lbl.setStyleSheet(f"font-size:11px; font-weight:700; color:{color}; text-align:right;")
#             row.addWidget(lbl); row.addWidget(bar_bg); row.addWidget(val_lbl)
#             lay.addLayout(row)


# class HelpCard(QFrame):
#     cmd_clicked = pyqtSignal(str)

#     def __init__(self, commands: list, parent=None):
#         super().__init__(parent)
#         lay = QVBoxLayout(self)
#         lay.setContentsMargins(8, 4, 8, 4)
#         lay.setSpacing(4)
#         for emoji, title, example in commands:
#             row = QPushButton()
#             row.setCursor(Qt.CursorShape.PointingHandCursor)
#             row.setStyleSheet(f"""
#                 QPushButton {{
#                     background:{C['bg3']}; border:1px solid {C['border']};
#                     border-radius:8px; text-align:left; padding:8px 12px;
#                 }}
#                 QPushButton:hover {{
#                     background:{C['blue_l']}; border-color:{C['blue']};
#                 }}
#             """)
#             rl = QHBoxLayout(row)
#             rl.setContentsMargins(0,0,0,0)
#             ic = QLabel(emoji)
#             ic.setFixedWidth(24)
#             ic.setStyleSheet("font-size:14px;")
#             tl = QVBoxLayout()
#             tl.setSpacing(1)
#             tl.addWidget(QLabel(f'<b style="font-size:13px">{title}</b>'))
#             ex = QLabel(f'<span style="color:{C["muted"]};font-size:11px">{example}</span>')
#             ex.setTextFormat(Qt.TextFormat.RichText)
#             tl.addWidget(ex)
#             rl.addWidget(ic); rl.addLayout(tl)
#             row.clicked.connect(lambda _, e=example.strip('"'): self.cmd_clicked.emit(e))
#             lay.addWidget(row)


# # ─── CHAT AREA ───────────────────────────────────────────────────────────────

# class ChatArea(QWidget):
#     send_message = pyqtSignal(str)

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setStyleSheet(f"background:{C['bg']};")
#         outer = QVBoxLayout(self)
#         outer.setContentsMargins(0,0,0,0)
#         outer.setSpacing(0)

#         # Scroll area
#         self.scroll = QScrollArea()
#         self.scroll.setWidgetResizable(True)
#         self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

#         self.msg_container = QWidget()
#         self.msg_container.setStyleSheet(f"background:{C['bg']};")
#         self.msg_layout = QVBoxLayout(self.msg_container)
#         self.msg_layout.setContentsMargins(16,16,16,10)
#         self.msg_layout.setSpacing(12)

#         self._add_welcome()

#         self.msg_layout.addStretch()
#         self.scroll.setWidget(self.msg_container)
#         outer.addWidget(self.scroll)

#         # Progress bar
#         self.progress_bar = QProgressBar()
#         self.progress_bar.setFixedHeight(3)
#         self.progress_bar.setTextVisible(False)
#         self.progress_bar.setStyleSheet(f"""
#             QProgressBar {{ background:{C['border']}; border:none; }}
#             QProgressBar::chunk {{ background:{C['blue']}; }}
#         """)
#         self.progress_bar.hide()
#         outer.addWidget(self.progress_bar)

#         self.status_bar = QLabel("")
#         self.status_bar.setStyleSheet(f"font-size:11px; color:{C['muted']}; padding:2px 16px;")
#         self.status_bar.hide()
#         outer.addWidget(self.status_bar)

#         outer.addWidget(self._build_input())

#     def _build_input(self) -> QWidget:
#         w = QWidget()
#         w.setStyleSheet(f"background:{C['bg2']}; border-top:1px solid {C['border']};")
#         outer = QVBoxLayout(w)
#         outer.setContentsMargins(14, 8, 14, 12)
#         outer.setSpacing(6)

#         # Hint chips
#         hints = QHBoxLayout()
#         hints.setSpacing(6)
#         for hint in ["🔍 Find file...", "💻 System status", "🔐 Security scan", "📦 Duplicates"]:
#             c = QPushButton(hint)
#             c.setCursor(Qt.CursorShape.PointingHandCursor)
#             c.setStyleSheet(f"""
#                 QPushButton {{
#                     background:{C['bg3']}; color:{C['text2']};
#                     border:1px solid {C['border']}; border-radius:14px;
#                     padding:3px 10px; font-size:11px;
#                 }}
#                 QPushButton:hover {{
#                     background:{C['blue_l']}; color:{C['blue']};
#                     border-color:{C['blue']};
#                 }}
#             """)
#             text = hint.split(" ", 1)[1].strip(".")
#             c.clicked.connect(lambda _, t=text: self._set_hint(t))
#             hints.addWidget(c)
#         hints.addStretch()
#         outer.addLayout(hints)

#         # Input row
#         row = QHBoxLayout()
#         row.setSpacing(8)

#         self.input = QTextEdit()
#         self.input.setFixedHeight(44)
#         self.input.setPlaceholderText("Ask ARIA anything about your system...")
#         self.input.setStyleSheet(f"""
#             QTextEdit {{
#                 background:{C['bg3']}; color:{C['text']};
#                 border:1.5px solid {C['border']}; border-radius:12px;
#                 padding:10px 14px; font-size:13px;
#                 selection-background-color:{C['blue']};
#             }}
#             QTextEdit:focus {{
#                 border-color:{C['blue']};
#                 background:{C['bg2']};
#             }}
#         """)
#         self.input.installEventFilter(self)

#         send = QPushButton("Send ➤")
#         send.setFixedHeight(44)
#         send.setMinimumWidth(90)
#         send.setCursor(Qt.CursorShape.PointingHandCursor)
#         send.setStyleSheet(f"""
#             QPushButton {{
#                 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
#                     stop:0 {C['blue']}, stop:1 #5B52E8);
#                 color:white; border:none; border-radius:12px;
#                 font-size:13px; font-weight:600; padding:0 16px;
#             }}
#             QPushButton:hover {{
#                 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
#                     stop:0 {C['blue_d']}, stop:1 #4A41D7);
#             }}
#             QPushButton:pressed {{ opacity:0.9; }}
#         """)
#         send.clicked.connect(self._send)

#         row.addWidget(self.input)
#         row.addWidget(send)
#         outer.addLayout(row)
#         return w

#     def eventFilter(self, obj, event):
#         from PyQt6.QtCore import QEvent
#         if obj == self.input and event.type() == QEvent.Type.KeyPress:
#             from PyQt6.QtGui import QKeyEvent
#             ke = event
#             if ke.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (ke.modifiers() & Qt.KeyboardModifier.ShiftModifier):
#                 self._send()
#                 return True
#         return super().eventFilter(obj, event)

#     def _send(self):
#         txt = self.input.toPlainText().strip()
#         if txt:
#             self.input.clear()
#             self.send_message.emit(txt)

#     def _set_hint(self, text: str):
#         self.input.setPlainText(text + " ")
#         self.input.setFocus()

#     def _add_welcome(self):
#         w = QFrame()
#         w.setStyleSheet(f"background:transparent; border:none;")
#         l = QVBoxLayout(w)
#         l.setSpacing(10)
#         l.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         ic = QLabel("◈")
#         ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         ic.setStyleSheet(f"font-size:42px; color:{C['blue']}; background:transparent;")

#         t1 = QLabel("Hello! I'm ARIA")
#         t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         t1.setStyleSheet(f"font-size:20px; font-weight:700; color:{C['text']}; background:transparent;")

#         t2 = QLabel("Your local, offline AI assistant for your operating system.\nNo cloud. No data leaving your machine.")
#         t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         t2.setStyleSheet(f"font-size:13px; color:{C['muted']}; background:transparent; line-height:1.6;")
#         t2.setWordWrap(True)

#         l.addWidget(ic)
#         l.addWidget(t1)
#         l.addWidget(t2)
#         self.msg_layout.addWidget(w)

#     def add_user_message(self, text: str):
#         self.msg_layout.insertWidget(self.msg_layout.count()-1, MessageBubble(text, "user"))
#         self._scroll_bottom()

#     def add_aria_response(self, result: dict):
#         # Remove typing indicator
#         self._remove_typing()

#         # Text bubble
#         txt = result.get("text", "")
#         if txt:
#             self.msg_layout.insertWidget(self.msg_layout.count()-1, MessageBubble(txt, "aria"))

#         # Data card
#         rtype = result.get("type", "")
#         data  = result.get("data")

#         if rtype == "file_results" and data:
#             fc = FileResultCard(data)
#             self.msg_layout.insertWidget(self.msg_layout.count()-1, fc)

#         elif rtype == "security_report" and data:
#             sc = SecurityCard(data)
#             self.msg_layout.insertWidget(self.msg_layout.count()-1, sc)

#         elif rtype == "system_status" and data:
#             sysc = SystemCard(data)
#             self.msg_layout.insertWidget(self.msg_layout.count()-1, sysc)

#         elif rtype == "help" and data:
#             hc = HelpCard(data.get("commands",[]))
#             hc.cmd_clicked.connect(self.send_message)
#             self.msg_layout.insertWidget(self.msg_layout.count()-1, hc)

#         self._scroll_bottom()

#     def show_typing(self):
#         dots = QLabel("  ● ● ●  ")
#         dots.setObjectName("typing")
#         dots.setStyleSheet(f"""
#             background:{C['bg2']}; color:{C['blue']};
#             border:1px solid {C['border']}; border-radius:14px;
#             padding:8px 16px; font-size:18px; letter-spacing:4px;
#             max-width:100px;
#         """)
#         row = QHBoxLayout()
#         av = QLabel("AR")
#         av.setFixedSize(28,28)
#         av.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         av.setStyleSheet(f"background:{C['bg3']}; color:{C['blue']}; border-radius:8px; font-size:9px; font-weight:700;")
#         row.addWidget(av)
#         row.addWidget(dots)
#         row.addStretch()
#         container = QWidget()
#         container.setObjectName("typing_container")
#         container.setLayout(row)
#         self.msg_layout.insertWidget(self.msg_layout.count()-1, container)
#         self._scroll_bottom()

#     def _remove_typing(self):
#         for i in range(self.msg_layout.count()):
#             item = self.msg_layout.itemAt(i)
#             if item and item.widget() and item.widget().objectName() == "typing_container":
#                 w = item.widget()
#                 self.msg_layout.removeWidget(w)
#                 w.deleteLater()
#                 return

#     def show_progress(self, val: int, total: int):
#         self.progress_bar.setMaximum(max(1, total))
#         self.progress_bar.setValue(val)
#         self.progress_bar.show()

#     def hide_progress(self):
#         self.progress_bar.hide()

#     def set_status(self, msg: str):
#         if msg:
#             self.status_bar.setText(msg)
#             self.status_bar.show()
#         else:
#             self.status_bar.hide()

#     def _scroll_bottom(self):
#         QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
#             self.scroll.verticalScrollBar().maximum()
#         ))


# # ─── MAIN WINDOW ─────────────────────────────────────────────────────────────

# class ARIAWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("ARIA — Autonomous Resident Intelligence Assistant")
#         self.resize(config.get("window_width",900), config.get("window_height",640))
#         self.setMinimumSize(720, 500)
#         self.setStyleSheet(STYLESHEET)

#         # Frameless for nicer look
#         self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
#         self._drag_pos = None

#         central = QWidget()
#         central.setObjectName("central")
#         self.setCentralWidget(central)
#         main_lay = QVBoxLayout(central)
#         main_lay.setContentsMargins(0, 0, 0, 0)
#         main_lay.setSpacing(0)

#         # Drop shadow effect via stylesheet
#         self.setStyleSheet(STYLESHEET + """
#             QMainWindow {
#                 border: 1px solid #DDE3F5;
#                 border-radius: 12px;
#             }
#         """)

#         # Header
#         self.header = Header()
#         self.header.settings_clicked.connect(self._open_settings)
#         self.header.index_clicked.connect(self._start_index)
#         self.header.minimize_clicked.connect(self.showMinimized)
#         self.header.close_clicked.connect(self._hide_to_tray)
#         main_lay.addWidget(self.header)

#         # Body
#         body = QHBoxLayout()
#         body.setContentsMargins(0,0,0,0)
#         body.setSpacing(0)

#         self.sidebar  = Sidebar()
#         self.chat     = ChatArea()

#         self.sidebar.quick_action.connect(self._on_quick_action)
#         self.chat.send_message.connect(self._on_message)

#         body.addWidget(self.sidebar)
#         body.addWidget(self.chat)

#         body_widget = QWidget()
#         body_widget.setLayout(body)
#         main_lay.addWidget(body_widget, 1)

#         # Init backend modules
#         self._init_modules()

#         # Global hotkey
#         self._hotkey = QShortcut(QKeySequence("Ctrl+Space"), self)
#         self._hotkey.activated.connect(self._toggle_visibility)

#         # Stats worker
#         self.stats_worker = StatsWorker(4000)
#         self.stats_worker.stats.connect(self._on_stats)
#         self.stats_worker.start()

#         # Auto-index if configured
#         if config.get("auto_index_on_start") and self.indexer.get_stats()["total_files"] == 0:
#             QTimer.singleShot(2000, self._start_index)

#     def _init_modules(self):
#         import sys, os
#         sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
#         from core.file_indexer    import FileIndexer
#         from core.system_security import SystemMonitor, SecurityScanner

#         self.indexer   = FileIndexer()
#         self.monitor   = SystemMonitor()
#         self.security  = SecurityScanner()
#         self.modules   = {
#             "indexer":   self.indexer,
#             "monitor":   self.monitor,
#             "security":  self.security,
#             "ollama_available": self._check_ollama(),
#         }

#         stats = self.indexer.get_stats()
#         if stats["total_files"] > 0:
#             self.sidebar.update_index(stats["total_files"])
#             self.header.set_status(True)

#     def _check_ollama(self) -> bool:
#         try:
#             import urllib.request
#             url = config.get("ollama_url") + "/api/tags"
#             urllib.request.urlopen(url, timeout=2)
#             return True
#         except Exception:
#             return False

#     def _on_message(self, text: str):
#         self.chat.add_user_message(text)
#         self.chat.show_typing()
#         worker = ChatWorker(text, self.modules)
#         worker.response.connect(self.chat.add_aria_response)
#         worker.error.connect(lambda e: self.chat.add_aria_response({
#             "type":"chat","text":f"Sorry, I ran into an error: {e}","data":None
#         }))
#         worker.start()
#         self._workers = getattr(self, '_workers', [])
#         self._workers.append(worker)

#     def _on_quick_action(self, cmd: str):
#         self._on_message(cmd)

#     def _start_index(self):
#         paths = config.get("index_paths", [])
#         if not paths:
#             self.chat.add_aria_response({"type":"chat","text":"No index paths configured. Open Settings → Indexing.","data":None})
#             return
#         self.chat.add_aria_response({"type":"chat","text":f"Starting to index **{paths[0]}** in the background...","data":None})

#         self.idx_worker = IndexWorker(paths[0], self.indexer)
#         self.idx_worker.progress.connect(self.chat.show_progress)
#         self.idx_worker.status.connect(self.chat.set_status)
#         self.idx_worker.finished.connect(self._on_index_done)
#         self.idx_worker.start()

#     def _on_index_done(self, count: int):
#         self.chat.hide_progress()
#         self.chat.set_status("")
#         self.sidebar.update_index(count)
#         self.header.set_status(True)
#         self.chat.add_aria_response({"type":"chat","text":f"✅ Done! I've indexed **{count:,} files**. You can now search for anything.","data":None})

#     def _on_stats(self, data: dict):
#         self.sidebar.update_stats(data)

#     def _open_settings(self):
#         from aria_settings import SettingsDialog
#         dlg = SettingsDialog(self)
#         dlg.exec()

#     def _hide_to_tray(self):
#         self.hide()

#     def _toggle_visibility(self):
#         if self.isVisible():
#             self.hide()
#         else:
#             self.show()
#             self.raise_()
#             self.activateWindow()

#     # ── Frameless dragging ────────────────────────────────────────────────
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton:
#             self._drag_pos = event.globalPosition().toPoint() - self.pos()

#     def mouseMoveEvent(self, event):
#         if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
#             self.move(event.globalPosition().toPoint() - self._drag_pos)

#     def mouseReleaseEvent(self, event):
#         self._drag_pos = None

#     def closeEvent(self, event):
#         config.set("window_width",  self.width())
#         config.set("window_height", self.height())
#         event.accept()


# Version 1.0.2
"""
ARIA Main Window — Production Grade PyQt6 UI
Fixes: font pt units, transparent backgrounds, proper data cards
"""
import sys, os, re, subprocess
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QScrollArea,
    QFrame, QProgressBar, QApplication, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore  import Qt, QTimer, pyqtSignal
from PyQt6.QtGui   import (QColor, QKeySequence, QShortcut, QCursor)

from aria_config  import config
from aria_workers import IndexWorker, ChatWorker, StatsWorker

# ─── PALETTE ─────────────────────────────────────────────────────────────────
P = {
    "bg":      "#F2F5FF",
    "bg2":     "#FFFFFF",
    "bg3":     "#E8EEFF",
    "border":  "#D4DCF5",
    "blue":    "#3B6FD4",
    "blue_h":  "#2A57B5",
    "blue_l":  "#EBF0FF",
    "purple":  "#6D4ADE",
    "green":   "#0A8A5A",
    "green_l": "#E6F7F1",
    "amber":   "#C96C0A",
    "amber_l": "#FEF5E7",
    "red":     "#C92020",
    "red_l":   "#FEECEC",
    "text":    "#141C2E",
    "text2":   "#3D4F6B",
    "muted":   "#7E93B8",
    "line":    "#E2E8F8",
}

# Use pt units throughout to avoid Windows DPI font-size warning
SS = f"""
* {{
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    color: {P['text']};
}}
QMainWindow, QWidget#root {{
    background: {P['bg']};
}}
QScrollBar:vertical {{
    background: transparent; width: 5px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {P['border']}; border-radius: 3px; min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QToolTip {{
    background: {P['text']}; color: white; border: none;
    padding: 4px 8px; border-radius: 4px; font-size: 9pt;
}}
"""

EXT_ICONS = {
    ".pdf":"📕",".doc":"📘",".docx":"📘",".xls":"📗",".xlsx":"📗",
    ".csv":"📊",".py":"🐍",".js":"🟨",".ts":"🔷",".html":"🌐",
    ".css":"🎨",".json":"📋",".jpg":"🖼",".jpeg":"🖼",".png":"🖼",
    ".gif":"🎞",".mp4":"🎬",".mp3":"🎵",".zip":"📦",".tar":"📦",
    ".txt":"📄",".md":"📝",".sh":"⚙",".bat":"⚙",".exe":"⚙",
    ".pptx":"📊",".odt":"📄",".sql":"🗃",".go":"🔵",".rs":"🦀",
}


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def lbl(text="", pt=10, bold=False, color=None, wrap=False) -> QLabel:
    w = QLabel(text)
    col = color or P["text"]
    wt  = "600" if bold else "400"
    w.setStyleSheet(
        f"background: transparent; color: {col}; "
        f"font-size: {pt}pt; font-weight: {wt}; border: none;"
    )
    if wrap:
        w.setWordWrap(True)
    return w


def hdivider() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {P['border']}; border: none; color: {P['border']};")
    return f


def pill(text: str, bg: str, fg: str) -> QLabel:
    w = QLabel(text)
    w.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 9px; "
        f"padding: 1px 7px; font-size: 8pt; font-weight: 600; border: none;"
    )
    return w


def btn_style(primary=False) -> str:
    if primary:
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {P['blue']}, stop:1 {P['purple']});
                color: white; border: none; border-radius: 9px;
                font-size: 10pt; font-weight: 700; padding: 6px 18px;
            }}
            QPushButton:hover {{ background: {P['blue_h']}; }}
        """
    return f"""
        QPushButton {{
            background: {P['bg3']}; color: {P['text2']};
            border: 1px solid {P['border']}; border-radius: 8px;
            font-size: 9pt; padding: 5px 14px;
        }}
        QPushButton:hover {{
            background: {P['blue_l']}; color: {P['blue']};
            border-color: {P['blue']};
        }}
    """


def open_path(path: str):
    if not path or not os.path.exists(path):
        return
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


# ─── HEADER ──────────────────────────────────────────────────────────────────
class Header(QWidget):
    sig_settings = pyqtSignal()
    sig_index    = pyqtSignal()
    sig_minimize = pyqtSignal()
    sig_close    = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)
        self.setStyleSheet(
            f"background: {P['bg2']}; "
            f"border-bottom: 1px solid {P['border']};"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(10)

        sym = lbl("◈", pt=18, bold=True, color=P['blue'])
        lay.addWidget(sym)

        name_c = QVBoxLayout()
        name_c.setSpacing(0)
        name_c.setContentsMargins(0, 0, 0, 0)
        name_w = QLabel("ARIA")
        name_w.setStyleSheet(
            f"background: transparent; font-size: 13pt; font-weight: 700; "
            f"color: {P['text']}; letter-spacing: 3px; border: none;"
        )
        sub_w = lbl("Autonomous Resident Intelligence", pt=8, color=P['muted'])
        name_c.addWidget(name_w)
        name_c.addWidget(sub_w)
        lay.addLayout(name_c)
        lay.addStretch()

        self._status = lbl("● OFFLINE", pt=9, color=P['muted'])
        lay.addWidget(self._status)

        for text, sig in [("⚡  Index Files", self.sig_index), ("⚙  Settings", self.sig_settings)]:
            b = QPushButton(text)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(btn_style())
            b.clicked.connect(sig)
            lay.addWidget(b)

        for txt, sig, hov in [("−", self.sig_minimize, P['amber']), ("✕", self.sig_close, P['red'])]:
            b = QPushButton(txt)
            b.setFixedSize(26, 26)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {P['bg3']}; color: {P['muted']};
                    border: 1px solid {P['border']}; border-radius: 13px;
                    font-size: 11pt; font-weight: 700;
                }}
                QPushButton:hover {{ background: {hov}; color: white; border-color: {hov}; }}
            """)
            b.clicked.connect(sig)
            lay.addWidget(b)

    def set_online(self, ok: bool):
        if ok:
            self._status.setText("●  READY")
            self._status.setStyleSheet(
                f"background: transparent; font-size: 9pt; color: {P['green']}; border: none;"
            )
        else:
            self._status.setText("●  OFFLINE")
            self._status.setStyleSheet(
                f"background: transparent; font-size: 9pt; color: {P['muted']}; border: none;"
            )


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
class StatBar(QWidget):
    def __init__(self, label: str, color: str):
        super().__init__()
        self.setFixedHeight(22)
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        title = lbl(label, pt=8, bold=True, color=P['muted'])
        title.setFixedWidth(34)
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._track = QFrame()
        self._track.setFixedSize(96, 4)
        self._track.setStyleSheet(
            f"background: {P['bg3']}; border-radius: 2px; border: none;"
        )
        self._fill = QFrame(self._track)
        self._fill.setGeometry(0, 0, 4, 4)
        self._fill.setStyleSheet(
            f"background: {color}; border-radius: 2px; border: none;"
        )
        self._color = color

        self._val = lbl("—", pt=9, bold=True, color=P['text2'])
        self._val.setFixedWidth(34)

        lay.addWidget(title)
        lay.addWidget(self._track)
        lay.addWidget(self._val)

    def update(self, pct: float):
        w = max(4, int(96 * pct / 100))
        self._fill.setGeometry(0, 0, w, 4)
        self._val.setText(f"{pct:.0f}%")


class QuickBtn(QPushButton):
    def __init__(self, icon: str, title: str, sub: str):
        super().__init__()
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(50)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 9px;
            }}
            QPushButton:hover {{
                background: {P['blue_l']};
                border-color: {P['border']};
            }}
        """)
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(10)

        ic = QLabel(icon)
        ic.setFixedSize(30, 30)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(
            f"background: {P['blue_l']}; border-radius: 7px; "
            f"font-size: 14pt; color: {P['blue']}; border: none;"
        )

        col = QVBoxLayout()
        col.setSpacing(1)
        col.setContentsMargins(0, 0, 0, 0)
        col.addWidget(lbl(title, pt=10, bold=True))
        col.addWidget(lbl(sub, pt=8, color=P['muted']))
        row.addWidget(ic)
        row.addLayout(col)
        row.addStretch()


class Sidebar(QWidget):
    sig_action = pyqtSignal(str)

    ACTIONS = [
        ("🔍", "Find File",     "By name or content",  "find file"),
        ("💻", "System Status", "CPU · RAM · Disk",    "how is my system"),
        ("🔐", "Security Scan", "Threats & anomalies", "run security scan"),
        ("📦", "Duplicates",    "Free up disk space",  "find duplicate files"),
        ("🕑", "Recent Files",  "Last modified",       "show recent files"),
        ("❓", "Help",          "All commands",        "help"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(218)
        self.setStyleSheet(
            f"background: {P['bg2']}; "
            f"border-right: 1px solid {P['border']};"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 12, 8, 10)
        lay.setSpacing(2)

        lay.addWidget(self._sec_lbl("QUICK ACTIONS"))
        for icon, title, sub, cmd in self.ACTIONS:
            b = QuickBtn(icon, title, sub)
            b.clicked.connect(lambda _, c=cmd: self.sig_action.emit(c))
            lay.addWidget(b)

        lay.addSpacing(6)
        lay.addWidget(hdivider())
        lay.addSpacing(6)
        lay.addWidget(self._sec_lbl("LIVE SYSTEM"))

        self._cpu  = StatBar("CPU",  P['blue'])
        self._ram  = StatBar("RAM",  P['purple'])
        self._disk = StatBar("DISK", P['amber'])
        for s in (self._cpu, self._ram, self._disk):
            lay.addWidget(s)

        lay.addStretch()

        self._idx = lbl("Index: not built", pt=8, color=P['muted'])
        self._idx.setContentsMargins(4, 0, 0, 4)
        lay.addWidget(self._idx)

    def _sec_lbl(self, text: str) -> QLabel:
        w = QLabel(text)
        w.setContentsMargins(4, 2, 0, 4)
        w.setStyleSheet(
            f"background: transparent; font-size: 8pt; font-weight: 700; "
            f"color: {P['muted']}; letter-spacing: 1px; border: none;"
        )
        return w

    def refresh_stats(self, d: dict):
        self._cpu.update(d.get("cpu", {}).get("percent", 0))
        self._ram.update(d.get("memory", {}).get("percent", 0))
        disks = d.get("disk") or [{}]
        self._disk.update(disks[0].get("percent", 0))

    def set_index(self, n: int):
        self._idx.setText(f"Index:  {n:,} files")
        self._idx.setStyleSheet(
            f"background: transparent; font-size: 8pt; "
            f"color: {P['green']}; padding-left: 4px; border: none;"
        )


# ─── DATA CARDS ──────────────────────────────────────────────────────────────
class FileResultsCard(QFrame):
    def __init__(self, files: list, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(5)

        for f in files[:12]:
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {P['bg2']};
                    border: 1px solid {P['border']};
                    border-radius: 9px;
                }}
                QFrame:hover {{
                    border-color: {P['blue']};
                    background: {P['blue_l']};
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(11, 8, 11, 8)
            rl.setSpacing(10)

            ic = QLabel(EXT_ICONS.get(f.get("extension", "").lower(), "📄"))
            ic.setFixedSize(28, 28)
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet("background: transparent; font-size: 15pt; border: none;")

            info = QVBoxLayout()
            info.setSpacing(2)
            info.setContentsMargins(0, 0, 0, 0)
            info.addWidget(lbl(f.get("name", ""), pt=10, bold=True))

            meta = QHBoxLayout()
            meta.setSpacing(5)
            meta.setContentsMargins(0, 0, 0, 0)
            dir_lbl = QLabel(f.get("directory", ""))
            dir_lbl.setStyleSheet(
                f"background: transparent; font-size: 8pt; color: {P['muted']}; "
                f"font-family: 'Consolas','Courier New',monospace; border: none;"
            )
            meta.addWidget(dir_lbl)
            for tag in (f.get("tags") or [])[:3]:
                meta.addWidget(pill(tag, P['blue_l'], P['blue']))
            if f.get("size"):
                meta.addWidget(pill(f["size"], P['bg3'], P['muted']))
            if f.get("modified"):
                meta.addWidget(pill(f["modified"], P['bg3'], P['muted']))
            meta.addStretch()
            info.addLayout(meta)

            rl.addWidget(ic)
            rl.addLayout(info)
            rl.addStretch()

            ob = QPushButton("Open")
            ob.setFixedSize(54, 26)
            ob.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            ob.setStyleSheet(f"""
                QPushButton {{
                    background: {P['bg3']}; color: {P['text2']};
                    border: 1px solid {P['border']}; border-radius: 6px;
                    font-size: 8pt; font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {P['blue_l']}; color: {P['blue']};
                    border-color: {P['blue']};
                }}
            """)
            fp = f.get("path", "")
            ob.clicked.connect(lambda _, p=fp: open_path(p))
            rl.addWidget(ob)
            lay.addWidget(row)


class DuplicatesCard(QFrame):
    """Duplicate file groups with full paths in a table."""

    def __init__(self, groups: list, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(10)

        total_mb = sum(g.get("wasted_mb", 0) for g in groups)

        # Summary banner
        banner = QFrame()
        banner.setStyleSheet(
            f"background: {P['amber_l']}; border: 1px solid #F0C070; border-radius: 9px;"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(14, 10, 14, 10)
        bl.addWidget(lbl(f"📦  {len(groups)} duplicate group(s) found", pt=10, bold=True, color=P['amber']))
        bl.addStretch()
        bl.addWidget(lbl(f"💾  {total_mb:.1f} MB recoverable", pt=10, bold=True, color=P['amber']))
        lay.addWidget(banner)

        for i, g in enumerate(groups[:20]):
            gf = QFrame()
            gf.setStyleSheet(
                f"background: {P['bg2']}; border: 1px solid {P['border']}; border-radius: 9px;"
            )
            gl = QVBoxLayout(gf)
            gl.setContentsMargins(12, 10, 12, 10)
            gl.setSpacing(7)

            # Group header
            hrow = QHBoxLayout()
            hrow.setSpacing(8)
            hrow.addWidget(lbl(f"Group {i + 1}", pt=9, bold=True, color=P['blue']))
            hrow.addWidget(lbl(
                f"·  {g.get('count', 0)} identical copies  ·  "
                f"{g.get('wasted_mb', 0):.2f} MB wasted  ·  MD5: {g.get('md5', '')[:12]}…",
                pt=9, color=P['muted']
            ))
            hrow.addStretch()
            gl.addLayout(hrow)

            files = g.get("files", [])
            tbl = QTableWidget(len(files), 3)
            tbl.setHorizontalHeaderLabels(["File Name", "Full Path", "Action"])
            tbl.horizontalHeader().setDefaultSectionSize(120)
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            tbl.setColumnWidth(2, 72)
            tbl.verticalHeader().setVisible(False)
            tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            tbl.setAlternatingRowColors(True)
            tbl.setShowGrid(False)
            tbl.setFixedHeight(min(32 * len(files) + 34, 180))
            tbl.setStyleSheet(f"""
                QTableWidget {{
                    background: {P['bg3']};
                    alternate-background-color: {P['bg2']};
                    border: none; border-radius: 6px;
                    font-size: 9pt; outline: none;
                    gridline-color: transparent;
                }}
                QHeaderView::section {{
                    background: {P['bg3']}; color: {P['muted']};
                    border: none; padding: 5px 8px;
                    font-size: 8pt; font-weight: 700;
                    letter-spacing: 0.5px;
                }}
                QTableWidget::item {{ padding: 4px 8px; border: none; }}
                QTableWidget::item:selected {{
                    background: {P['blue_l']}; color: {P['blue']};
                }}
            """)

            from pathlib import Path
            for r, fpath in enumerate(files):
                p = Path(fpath)
                ni = QTableWidgetItem(p.name)
                ni.setToolTip(fpath)
                pi = QTableWidgetItem(str(p.parent))
                pi.setToolTip(fpath)
                tbl.setItem(r, 0, ni)
                tbl.setItem(r, 1, pi)

                ob = QPushButton("Open")
                ob.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                ob.setStyleSheet(f"""
                    QPushButton {{
                        background: {P['blue_l']}; color: {P['blue']};
                        border: none; border-radius: 5px;
                        font-size: 8pt; font-weight: 600;
                        padding: 3px 8px; margin: 3px;
                    }}
                    QPushButton:hover {{ background: {P['blue']}; color: white; }}
                """)
                ob.clicked.connect(lambda _, fp=fpath: open_path(fp))
                tbl.setCellWidget(r, 2, ob)
                tbl.setRowHeight(r, 30)

            gl.addWidget(tbl)
            lay.addWidget(gf)


class SystemCard(QFrame):
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(8)

        cpu   = data.get("cpu", {})
        mem   = data.get("memory", {})
        disks = data.get("disk") or []
        sys_  = data.get("system", {})
        bat   = data.get("battery")
        procs = data.get("top_processes", [])
        score = data.get("health_score", 100)
        alerts = data.get("alerts", [])

        sc = P['green'] if score >= 80 else P['amber'] if score >= 50 else P['red']
        sl = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 50 else "Poor"

        # Health banner
        banner = QFrame()
        banner.setStyleSheet(
            f"background: {sc}20; border: 1px solid {sc}50; border-radius: 9px;"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(14, 10, 14, 10)
        bl.addWidget(lbl(f"System Health  {score}/100  —  {sl}", pt=11, bold=True, color=sc))
        bl.addStretch()
        sysinfo = f"{sys_.get('os', '')}  ·  {sys_.get('hostname', '')}  ·  ⏱ {sys_.get('uptime', '')}"
        bl.addWidget(lbl(sysinfo, pt=9, color=P['muted']))
        lay.addWidget(banner)

        # Metrics grid
        grid = QFrame()
        grid.setStyleSheet(
            f"background: {P['bg2']}; border: 1px solid {P['border']}; border-radius: 9px;"
        )
        gl = QHBoxLayout(grid)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(0)

        metrics = [
            ("CPU", f"{cpu.get('percent', 0):.0f}%",
             f"{cpu.get('cores_physical', 1)} cores",
             cpu.get("percent", 0), P['blue']),
            ("MEMORY", f"{mem.get('used_gb', 0):.1f} GB",
             f"of {mem.get('total_gb', 0):.1f} GB  ({mem.get('percent', 0):.0f}%)",
             mem.get("percent", 0), P['purple']),
        ]
        for d in disks[:1]:
            metrics.append(("DISK", f"{d.get('used_gb', 0):.1f} GB",
                f"of {d.get('total_gb', 0):.1f} GB  ({d.get('percent', 0):.0f}%)",
                d.get("percent", 0), P['amber']))
        if bat:
            bat_sub = "Charging 🔌" if bat.get("plugged") else f"{bat.get('time_left', '?')} left"
            metrics.append(("BATTERY", f"{bat.get('percent', 0):.0f}%",
                bat_sub, bat.get("percent", 50), P['green']))

        for idx, (name, val, sub, pct, col) in enumerate(metrics):
            if idx > 0:
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet(f"background: {P['line']}; border: none;")
                gl.addWidget(sep)

            cell = QWidget()
            cell.setStyleSheet("background: transparent; border: none;")
            cl = QVBoxLayout(cell)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(4)

            cl.addWidget(lbl(name, pt=8, bold=True, color=P['muted']))

            c_val = col if pct < 85 else (P['red'] if pct > 92 else P['amber'])
            vrow = QHBoxLayout()
            vrow.setSpacing(6)
            dot = QFrame()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(
                f"background: {c_val}; border-radius: 4px; border: none;"
            )
            vrow.addWidget(dot)
            vrow.addWidget(lbl(val, pt=15, bold=True, color=P['text']))
            vrow.addStretch()
            cl.addLayout(vrow)
            cl.addWidget(lbl(sub, pt=8, color=P['muted']))

            bar_bg = QFrame()
            bar_bg.setFixedHeight(3)
            bar_bg.setStyleSheet(f"background: {P['bg3']}; border-radius: 2px; border: none;")
            bar = QFrame(bar_bg)
            bar.setFixedHeight(3)
            bar.setStyleSheet(f"background: {c_val}; border-radius: 2px; border: none;")
            bar.resize(max(4, int(160 * pct / 100)), 3)
            bar.move(0, 0)
            cl.addWidget(bar_bg)
            gl.addWidget(cell, 1)

        lay.addWidget(grid)

        # Top processes table
        if procs:
            pf = QFrame()
            pf.setStyleSheet(
                f"background: {P['bg2']}; border: 1px solid {P['border']}; border-radius: 9px;"
            )
            pl = QVBoxLayout(pf)
            pl.setContentsMargins(14, 10, 14, 10)
            pl.setSpacing(5)
            pl.addWidget(lbl("TOP PROCESSES", pt=8, bold=True, color=P['muted']))

            tbl = QTableWidget(min(len(procs), 6), 4)
            tbl.setHorizontalHeaderLabels(["Process", "PID", "CPU %", "RAM %"])
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            tbl.verticalHeader().setVisible(False)
            tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            tbl.setShowGrid(False)
            tbl.setAlternatingRowColors(True)
            tbl.setFixedHeight(min(30 * min(len(procs), 6) + 32, 220))
            tbl.setStyleSheet(f"""
                QTableWidget {{
                    background: {P['bg3']}; alternate-background-color: {P['bg2']};
                    border: none; font-size: 9pt; outline: none;
                }}
                QHeaderView::section {{
                    background: {P['bg3']}; color: {P['muted']};
                    border: none; padding: 4px 8px; font-size: 8pt; font-weight: 700;
                }}
                QTableWidget::item {{ padding: 4px 8px; border: none; }}
            """)
            for r, p in enumerate(procs[:6]):
                tbl.setItem(r, 0, QTableWidgetItem(p.get("name", "")))
                tbl.setItem(r, 1, QTableWidgetItem(str(p.get("pid", ""))))
                ci = QTableWidgetItem(f"{p.get('cpu', 0):.1f}%")
                ci.setForeground(QColor(P['blue']))
                tbl.setItem(r, 2, ci)
                mi = QTableWidgetItem(f"{p.get('mem', 0):.1f}%")
                mi.setForeground(QColor(P['purple']))
                tbl.setItem(r, 3, mi)
                tbl.setRowHeight(r, 28)
            pl.addWidget(tbl)
            lay.addWidget(pf)

        for a in alerts:
            col = P['red'] if a.get("level") == "critical" else P['amber']
            af = QFrame()
            af.setStyleSheet(
                f"background: {col}15; border: 1px solid {col}45; border-radius: 7px;"
            )
            al = QHBoxLayout(af)
            al.setContentsMargins(12, 8, 12, 8)
            icon = "🔴" if a.get("level") == "critical" else "⚠️"
            al.addWidget(lbl(f"{icon}  {a.get('message', '')}", pt=10, color=col))
            lay.addWidget(af)


class SecurityCard(QFrame):
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(8)

        risk  = data.get("risk_score", 0)
        col   = P['green'] if risk == 0 else (P['amber'] if risk < 50 else P['red'])
        badge = "ALL CLEAR" if risk == 0 else ("LOW RISK" if risk < 30 else ("MODERATE" if risk < 70 else "HIGH RISK"))

        banner = QFrame()
        banner.setStyleSheet(
            f"background: {col}15; border: 1px solid {col}45; border-radius: 9px;"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(14, 10, 14, 10)
        bl.addWidget(lbl(f"Risk Score:  {risk} / 100", pt=12, bold=True, color=col))
        bl.addStretch()
        bg_w = QLabel(badge)
        bg_w.setStyleSheet(
            f"background: {col}; color: white; border-radius: 9px; "
            f"padding: 3px 10px; font-size: 8pt; font-weight: 700; border: none;"
        )
        bl.addWidget(bg_w)
        lay.addWidget(banner)

        summary = data.get("summary", "")
        if summary:
            sl = lbl(summary, pt=10, color=P['text2'], wrap=True)
            lay.addWidget(sl)

        procs = data.get("suspicious_processes", [])
        if procs:
            pf = QFrame()
            pf.setStyleSheet(
                f"background: {P['red_l']}; border: 1px solid #F0AAAA; border-radius: 8px;"
            )
            pl = QVBoxLayout(pf)
            pl.setContentsMargins(12, 8, 12, 8)
            pl.setSpacing(4)
            pl.addWidget(lbl(f"🔴  {len(procs)} Suspicious Process(es)", pt=10, bold=True, color=P['red']))
            for p in procs:
                pl.addWidget(lbl(f"  • {p.get('name', '')}  (PID {p.get('pid', '')})  —  {p.get('exe', '?')}", pt=9, color=P['red']))
            lay.addWidget(pf)

        ports = data.get("open_ports", [])[:15]
        if ports:
            portf = QFrame()
            portf.setStyleSheet(
                f"background: {P['bg2']}; border: 1px solid {P['border']}; border-radius: 8px;"
            )
            pl2 = QVBoxLayout(portf)
            pl2.setContentsMargins(12, 10, 12, 10)
            pl2.setSpacing(6)
            susp = [p for p in ports if p.get("suspicious")]
            pl2.addWidget(lbl(
                f"🔌  {len(ports)} Listening Port(s)"
                + (f"  ·  {len(susp)} flagged suspicious" if susp else "  ·  All normal"),
                pt=10, bold=True
            ))
            tbl = QTableWidget(len(ports), 3)
            tbl.setHorizontalHeaderLabels(["Port", "Process", "Status"])
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            tbl.verticalHeader().setVisible(False)
            tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            tbl.setShowGrid(False)
            tbl.setAlternatingRowColors(True)
            tbl.setFixedHeight(min(30 * len(ports) + 34, 200))
            tbl.setStyleSheet(f"""
                QTableWidget {{
                    background: {P['bg3']}; alternate-background-color: {P['bg2']};
                    border: none; font-size: 9pt; outline: none;
                }}
                QHeaderView::section {{
                    background: {P['bg3']}; color: {P['muted']};
                    border: none; padding: 4px 8px; font-size: 8pt; font-weight: 700;
                }}
                QTableWidget::item {{ padding: 4px 8px; border: none; }}
            """)
            for r, p in enumerate(ports):
                tbl.setItem(r, 0, QTableWidgetItem(str(p.get("port", ""))))
                tbl.setItem(r, 1, QTableWidgetItem(p.get("process", "?")))
                status_txt = "⚠ Suspicious" if p.get("suspicious") else "✓ Normal"
                si = QTableWidgetItem(status_txt)
                si.setForeground(QColor(P['red'] if p.get("suspicious") else P['green']))
                tbl.setItem(r, 2, si)
                tbl.setRowHeight(r, 28)
            pl2.addWidget(tbl)
            lay.addWidget(portf)

        for ch in data.get("integrity_changes", []):
            cf = QFrame()
            cf.setStyleSheet(f"background: {P['red_l']}; border: 1px solid #F0AAAA; border-radius: 8px;")
            cl = QHBoxLayout(cf)
            cl.setContentsMargins(12, 8, 12, 8)
            cl.addWidget(lbl(f"🔴  Critical file modified:  {ch.get('file', '')}", pt=10, bold=True, color=P['red']))
            lay.addWidget(cf)

        usb = data.get("usb_devices", [])
        if usb:
            uf = QFrame()
            uf.setStyleSheet(f"background: {P['amber_l']}; border: 1px solid #E8C060; border-radius: 8px;")
            ul = QVBoxLayout(uf)
            ul.setContentsMargins(12, 8, 12, 8)
            ul.setSpacing(3)
            ul.addWidget(lbl(f"🔌  {len(usb)} USB Device(s) Connected", pt=10, bold=True, color=P['amber']))
            for d in usb:
                ul.addWidget(lbl(f"  • {d.get('device', '')}  →  {d.get('mountpoint', '')}  ({d.get('size_gb', 0):.1f} GB)", pt=9, color=P['amber']))
            lay.addWidget(uf)

        logins = data.get("failed_logins", [])
        if logins:
            lf = QFrame()
            lf.setStyleSheet(f"background: {P['red_l']}; border: 1px solid #F0AAAA; border-radius: 8px;")
            ll = QVBoxLayout(lf)
            ll.setContentsMargins(12, 8, 12, 8)
            ll.setSpacing(3)
            ll.addWidget(lbl(f"⚠  {len(logins)} Failed Login Attempt(s)", pt=10, bold=True, color=P['red']))
            for entry in logins[:5]:
                ll.addWidget(lbl(f"  {entry[:120]}", pt=8, color=P['red']))
            lay.addWidget(lf)


class HelpCard(QFrame):
    sig_click = pyqtSignal(str)

    def __init__(self, commands: list, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(5)

        for emoji, title, example in commands:
            btn = QPushButton()
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(46)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {P['bg2']}; border: 1px solid {P['border']};
                    border-radius: 8px; text-align: left; padding: 0;
                }}
                QPushButton:hover {{
                    background: {P['blue_l']}; border-color: {P['blue']};
                }}
            """)
            row = QHBoxLayout(btn)
            row.setContentsMargins(12, 0, 12, 0)
            row.setSpacing(10)
            row.addWidget(lbl(emoji, pt=12))
            col = QVBoxLayout()
            col.setSpacing(1)
            col.setContentsMargins(0, 0, 0, 0)
            col.addWidget(lbl(title, pt=10, bold=True))
            col.addWidget(lbl(example, pt=8, color=P['muted']))
            row.addLayout(col)
            row.addStretch()
            btn.clicked.connect(lambda _, ex=example.strip('"'): self.sig_click.emit(ex))
            lay.addWidget(btn)


# ─── CHAT BUBBLE ─────────────────────────────────────────────────────────────
def _md_to_html(text: str, is_user: bool) -> str:
    muted    = "#B0CAFF" if is_user else P['muted']
    code_bg  = "#FFFFFF20" if is_user else "#F1F5F9"
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`(.*?)`',
        f'<code style="background:{code_bg};padding:1px 4px;border-radius:3px;'
        f'font-family:Consolas,monospace;font-size:9pt;">'
        r'\1</code>', text)
    text = re.sub(r'^• (.+)$',
        r'<span style="color:' + muted + r'">▸</span> \1',
        text, flags=re.MULTILINE)
    text = text.replace('\n', '<br>')
    return text


class Bubble(QFrame):
    def __init__(self, text: str, role: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(3)

        is_user = role == "user"
        row = QHBoxLayout()
        row.setSpacing(10)
        if is_user:
            row.addStretch()

        av = QLabel("YOU" if is_user else "AR")
        av.setFixedSize(30, 30)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(f"""
            background: {"#3B6FD4" if is_user else P['bg3']};
            color: {"white" if is_user else P['blue']};
            border-radius: 8px; font-size: 7pt; font-weight: 700;
            letter-spacing: 0.5px; border: none;
        """)

        bubble = QLabel()
        bubble.setWordWrap(True)
        bubble.setTextFormat(Qt.TextFormat.RichText)
        bubble.setText(_md_to_html(text, is_user))
        bubble.setMaximumWidth(500)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        br = "14px 3px 14px 14px" if is_user else "3px 14px 14px 14px"
        bubble.setStyleSheet(f"""
            background: {"#3B6FD4" if is_user else P['bg2']};
            color: {"white" if is_user else P['text']};
            border: 1px solid {"#3B6FD4" if is_user else P['border']};
            border-radius: {br};
            padding: 9px 13px;
            font-size: 10pt;
            line-height: 1.6;
        """)

        if is_user:
            row.addWidget(bubble)
            row.addWidget(av)
        else:
            row.addWidget(av)
            row.addWidget(bubble)
            row.addStretch()

        outer.addLayout(row)

        from datetime import datetime
        ts = lbl(datetime.now().strftime("%H:%M"), pt=8, color=P['muted'])
        if is_user:
            ts_row = QHBoxLayout()
            ts_row.addStretch()
            ts_row.addWidget(ts)
            outer.addLayout(ts_row)
        else:
            outer.addWidget(ts)


class TypingBubble(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("typing_w")
        self.setStyleSheet("background: transparent; border: none;")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        av = QLabel("AR")
        av.setFixedSize(30, 30)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            f"background: {P['bg3']}; color: {P['blue']}; border-radius: 8px; "
            f"font-size: 7pt; font-weight: 700; border: none;"
        )
        dots = QLabel("●  ●  ●")
        dots.setStyleSheet(f"""
            background: {P['bg2']};
            color: {P['blue']};
            border: 1px solid {P['border']};
            border-radius: 14px;
            padding: 8px 18px;
            font-size: 10pt;
            letter-spacing: 4px;
        """)
        row.addWidget(av)
        row.addWidget(dots)
        row.addStretch()


# ─── CHAT AREA ───────────────────────────────────────────────────────────────
class ChatArea(QWidget):
    sig_send = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {P['bg']};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"background: {P['bg']};")

        self._msgs_w = QWidget()
        self._msgs_w.setStyleSheet(f"background: {P['bg']};")
        self._msgs_l = QVBoxLayout(self._msgs_w)
        self._msgs_l.setContentsMargins(20, 20, 20, 10)
        self._msgs_l.setSpacing(12)
        self._add_welcome()
        self._msgs_l.addStretch()

        self._scroll.setWidget(self._msgs_w)
        outer.addWidget(self._scroll)

        self._prog = QProgressBar()
        self._prog.setFixedHeight(3)
        self._prog.setTextVisible(False)
        self._prog.setStyleSheet(f"""
            QProgressBar {{ background: {P['border']}; border: none; }}
            QProgressBar::chunk {{ background: {P['blue']}; border-radius: 1px; }}
        """)
        self._prog.hide()
        outer.addWidget(self._prog)

        self._status_lbl = lbl("", pt=8, color=P['muted'])
        self._status_lbl.setContentsMargins(20, 2, 20, 2)
        self._status_lbl.hide()
        outer.addWidget(self._status_lbl)

        outer.addWidget(self._build_input())

    def _add_welcome(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setSpacing(10)
        l.setContentsMargins(0, 40, 0, 20)

        sym = lbl("◈", pt=36, bold=True, color=P['blue'])
        sym.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = lbl("Hello! I'm ARIA", pt=18, bold=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = lbl(
            "Your local, offline AI assistant for your operating system.\n"
            "No cloud. No data leaving your machine.",
            pt=10, color=P['muted'], wrap=True
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setMaximumWidth(360)

        l.addWidget(sym); l.addWidget(title); l.addWidget(sub)
        l.addSpacing(8)

        chips_row = QHBoxLayout()
        chips_row.setSpacing(8)
        chips_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for text, cmd in [
            ("🔍 Find my resume",  "where is my resume"),
            ("💻 System health",   "how is my system"),
            ("🔐 Security check",  "run security scan"),
            ("📦 Find duplicates", "find duplicate files"),
        ]:
            ch = QPushButton(text)
            ch.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            ch.setStyleSheet(f"""
                QPushButton {{
                    background: {P['bg2']}; color: {P['text2']};
                    border: 1px solid {P['border']}; border-radius: 16px;
                    padding: 6px 14px; font-size: 9pt; font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {P['blue_l']}; color: {P['blue']};
                    border-color: {P['blue']};
                }}
            """)
            ch.clicked.connect(lambda _, c=cmd: self.sig_send.emit(c))
            chips_row.addWidget(ch)

        cw = QWidget()
        cw.setStyleSheet("background: transparent;")
        cw.setLayout(chips_row)
        l.addWidget(cw)
        self._msgs_l.addWidget(w)

    def _build_input(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(
            f"background: {P['bg2']}; border-top: 1px solid {P['border']};"
        )
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 8, 16, 12)
        lay.setSpacing(6)

        hints = QHBoxLayout()
        hints.setSpacing(6)
        for text, cmd in [
            ("🔍 Find file…",    "find file "),
            ("💻 System status", "how is my system"),
            ("🔐 Security scan", "run security scan"),
            ("📦 Duplicates",    "find duplicate files"),
        ]:
            hc = QPushButton(text)
            hc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            hc.setStyleSheet(f"""
                QPushButton {{
                    background: {P['bg3']}; color: {P['text2']};
                    border: 1px solid {P['border']}; border-radius: 12px;
                    padding: 3px 10px; font-size: 8pt;
                }}
                QPushButton:hover {{
                    background: {P['blue_l']}; color: {P['blue']};
                    border-color: {P['blue']};
                }}
            """)
            hc.clicked.connect(lambda _, c=cmd: self._set_hint(c))
            hints.addWidget(hc)
        hints.addStretch()
        lay.addLayout(hints)

        row = QHBoxLayout()
        row.setSpacing(8)

        self._input = QTextEdit()
        self._input.setFixedHeight(46)
        self._input.setPlaceholderText("Ask ARIA anything about your system…")
        self._input.setStyleSheet(f"""
            QTextEdit {{
                background: {P['bg3']}; color: {P['text']};
                border: 1.5px solid {P['border']}; border-radius: 11px;
                padding: 10px 14px; font-size: 10pt;
                selection-background-color: {P['blue']};
            }}
            QTextEdit:focus {{
                border-color: {P['blue']};
                background: {P['bg2']};
            }}
        """)
        self._input.installEventFilter(self)

        send = QPushButton("Send  ➤")
        send.setFixedSize(90, 46)
        send.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        send.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {P['blue']}, stop:1 {P['purple']});
                color: white; border: none; border-radius: 11px;
                font-size: 10pt; font-weight: 700;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {P['blue_h']}, stop:1 #5A3AC0);
            }}
        """)
        send.clicked.connect(self._send)
        row.addWidget(self._input)
        row.addWidget(send)
        lay.addLayout(row)
        return w

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) \
               and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self._send()
                return True
        return super().eventFilter(obj, event)

    def _send(self):
        txt = self._input.toPlainText().strip()
        if txt:
            self._input.clear()
            self.sig_send.emit(txt)

    def _set_hint(self, text: str):
        self._input.setPlainText(text)
        self._input.setFocus()
        cur = self._input.textCursor()
        cur.movePosition(cur.MoveOperation.End)
        self._input.setTextCursor(cur)

    def _insert(self, w: QWidget):
        self._msgs_l.insertWidget(self._msgs_l.count() - 1, w)
        self._scroll_bottom()

    def _remove_typing(self):
        for i in range(self._msgs_l.count()):
            it = self._msgs_l.itemAt(i)
            if it and it.widget() and it.widget().objectName() == "typing_w":
                w = it.widget()
                self._msgs_l.removeWidget(w)
                w.deleteLater()
                return

    def _scroll_bottom(self):
        QTimer.singleShot(60, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def add_user(self, text: str):
        self._insert(Bubble(text, "user"))

    def add_response(self, result: dict):
        self._remove_typing()
        txt   = result.get("text", "")
        rtype = result.get("type", "chat")
        data  = result.get("data")
        if txt:
            self._insert(Bubble(txt, "aria"))
        if rtype == "file_results" and data:
            self._insert(FileResultsCard(data))
        elif rtype == "duplicates" and data:
            self._insert(DuplicatesCard(data))
        elif rtype == "system_status" and data:
            self._insert(SystemCard(data))
        elif rtype == "security_report" and data:
            self._insert(SecurityCard(data))
        elif rtype == "help" and data:
            hc = HelpCard(data.get("commands", []))
            hc.sig_click.connect(self.sig_send)
            self._insert(hc)
        self._scroll_bottom()

    def show_typing(self):
        self._insert(TypingBubble())

    def show_progress(self, done: int, total: int):
        self._prog.setMaximum(max(1, total))
        self._prog.setValue(done)
        self._prog.show()

    def hide_progress(self):
        self._prog.hide()

    def set_status_msg(self, msg: str):
        if msg:
            self._status_lbl.setText(msg)
            self._status_lbl.show()
        else:
            self._status_lbl.hide()


# ─── MAIN WINDOW ─────────────────────────────────────────────────────────────
class ARIAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ARIA")
        self.resize(config.get("window_width", 920), config.get("window_height", 650))
        self.setMinimumSize(760, 520)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(SS + f"""
            QMainWindow {{
                background: {P['bg']};
                border: 1px solid {P['border']};
                border-radius: 10px;
            }}
        """)

        self._drag = None
        self._workers = []

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        rl = QVBoxLayout(root)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self.header = Header()
        self.header.sig_settings.connect(self._open_settings)
        self.header.sig_index.connect(self._start_index)
        self.header.sig_minimize.connect(self.showMinimized)
        self.header.sig_close.connect(self._hide_to_tray)
        rl.addWidget(self.header)

        body = QWidget()
        body.setStyleSheet(f"background: {P['bg']};")
        bl = QHBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(0)

        self.sidebar = Sidebar()
        self.chat    = ChatArea()
        self.sidebar.sig_action.connect(self._on_message)
        self.chat.sig_send.connect(self._on_message)
        bl.addWidget(self.sidebar)
        bl.addWidget(self.chat, 1)
        rl.addWidget(body, 1)

        self._init_backend()
        QShortcut(QKeySequence("Ctrl+Space"), self).activated.connect(self._toggle)

        self._stats_w = StatsWorker(4000)
        self._stats_w.stats.connect(self.sidebar.refresh_stats)
        self._stats_w.start()

        if config.get("auto_index_on_start") and \
           self.indexer.get_stats()["total_files"] == 0:
            QTimer.singleShot(2000, self._start_index)

    def _init_backend(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))
        from core.file_indexer    import FileIndexer
        from core.system_security import SystemMonitor, SecurityScanner
        self.indexer  = FileIndexer()
        self.monitor  = SystemMonitor()
        self.security = SecurityScanner()
        self.modules  = {
            "indexer":          self.indexer,
            "monitor":          self.monitor,
            "security":         self.security,
            "ollama_available": self._ping_ollama(),
        }
        n = self.indexer.get_stats()["total_files"]
        if n:
            self.sidebar.set_index(n)
            self.header.set_online(True)

    def _ping_ollama(self) -> bool:
        try:
            import urllib.request
            urllib.request.urlopen(
                config.get("ollama_url", "http://localhost:11434") + "/api/tags", timeout=2
            )
            return True
        except Exception:
            return False

    def _on_message(self, text: str):
        self.chat.add_user(text)
        self.chat.show_typing()
        w = ChatWorker(text, self.modules)
        w.response.connect(self.chat.add_response)
        w.error.connect(lambda e: self.chat.add_response({
            "type": "chat", "text": f"Error: {e}", "data": None
        }))
        w.start()
        self._workers.append(w)
        self._workers = [wk for wk in self._workers if wk.isRunning()]

    def _start_index(self):
        paths = config.get("index_paths", [])
        if not paths:
            self.chat.add_response({
                "type": "chat",
                "text": "⚠️ No index paths configured. Go to **Settings → Indexing** and add a folder.",
                "data": None,
            })
            return
        self.chat.add_response({
            "type": "chat",
            "text": f"⚡ Indexing **{paths[0]}** — this runs in the background, I'll notify you when done…",
            "data": None,
        })
        self._idx = IndexWorker(paths[0], self.indexer)
        self._idx.progress.connect(self.chat.show_progress)
        self._idx.status.connect(self.chat.set_status_msg)
        self._idx.finished.connect(self._index_done)
        self._idx.start()

    def _index_done(self, count: int):
        self.chat.hide_progress()
        self.chat.set_status_msg("")
        self.sidebar.set_index(count)
        self.header.set_online(True)
        self.chat.add_response({
            "type": "chat",
            "text": f"✅ Indexing complete!  **{count:,} files** indexed and ready to search.",
            "data": None,
        })

    def _open_settings(self):
        from aria_settings import SettingsDialog
        SettingsDialog(self).exec()

    def _hide_to_tray(self):
        self.hide()

    def _toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show(); self.raise_(); self.activateWindow()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    def closeEvent(self, e):
        config.set("window_width",  self.width())
        config.set("window_height", self.height())
        self._stats_w.stop()
        e.accept()