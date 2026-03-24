# """
# ARIA Intent Engine — routes natural language to the right module
# and generates accurate, structured responses.
# """
# import re, os, subprocess, datetime
# from typing import Dict, Optional, List
# from pathlib import Path


# # ─── Intent patterns ─────────────────────────────────────────────────────────

# INTENTS = {
#     "file_name":    [r"where is", r"find file", r"locate file", r"search file",
#                      r"find my", r"where('s| is) my", r"look for file", r"get file"],
#     "file_content": [r"find.*about", r"file.*contain", r"file.*related to",
#                      r"file.*with content", r"search.*content", r"find content",
#                      r"file about", r"document about"],
#     "file_recent":  [r"recent files?", r"last.*files?", r"files? i (worked|opened|used) recently"],
#     "duplicates":   [r"duplicate", r"same files?", r"redundant files?", r"free.*space", r"clean.*disk"],
#     "system":       [r"system (status|info|health|performance|stats|check)",
#                      r"how is my (system|pc|computer|machine)", r"cpu|ram|memory|disk (usage|space|status)",
#                      r"battery", r"uptime", r"what.*running", r"check system"],
#     "processes":    [r"running processes?", r"what.*processes?", r"top processes?", r"task manager"],
#     "security":     [r"security (scan|check|status)", r"scan.*threat", r"check.*threat",
#                      r"malware|virus|hack|threat|suspicious", r"open ports?", r"is.*safe"],
#     "open_file":    [r"open (the |this |my )?file", r"launch", r"start"],
#     "disk_space":   [r"disk space", r"storage", r"how much.*space", r"free space"],
#     "help":         [r"help", r"what can you", r"commands?", r"features?", r"capabilities?",
#                      r"what do you (do|know)", r"how (do i|to) use"],
#     "greeting":     [r"^(hi|hello|hey|good morning|good afternoon|good evening|howdy)"],
#     "thanks":       [r"^(thanks?|thank you|thx|ty|great|nice|awesome|perfect)"],
# }


# def detect_intent(text: str) -> Optional[str]:
#     t = text.lower().strip()
#     for intent, patterns in INTENTS.items():
#         for pat in patterns:
#             if re.search(pat, t):
#                 return intent
#     return None


# def extract_query(text: str) -> str:
#     """Strip out intent keywords to get the core query."""
#     t = text.lower().strip()
#     remove = [
#         "where is", "where's", "find file", "find my", "find the", "find",
#         "locate", "search for", "look for", "get", "file about", "file containing",
#         "file with content", "find content", "document about", "search",
#         "please", "can you", "could you", "i need", "i want", "show me",
#         "my file", "file called", "file named", "named", "called", "file",
#     ]
#     for r in sorted(remove, key=len, reverse=True):
#         t = t.replace(r, " ")
#     return re.sub(r'\s+', ' ', t).strip(" ?.,!")


# def build_response(message: str, modules: Dict) -> Dict:
#     """Main dispatcher. Returns a structured response dict."""
#     intent = detect_intent(message)
#     query  = extract_query(message)

#     if intent == "greeting":
#         return {
#             "type": "chat",
#             "text": _greeting(),
#             "data": None,
#         }

#     if intent == "thanks":
#         return {
#             "type": "chat",
#             "text": "You're welcome! Let me know if there's anything else I can help with.",
#             "data": None,
#         }

#     if intent == "help":
#         return _help_response()

#     if intent in ("file_name", "file_content"):
#         return _file_search(query, intent, modules)

#     if intent == "file_recent":
#         return _recent_files(modules)

#     if intent == "duplicates":
#         return _duplicates(modules)

#     if intent in ("system", "disk_space"):
#         return _system_status(modules)

#     if intent == "processes":
#         return _processes(modules)

#     if intent == "security":
#         return _security(modules)

#     # Fallback: try file search anyway if query looks like a filename
#     if len(query) > 2 and not query.startswith("-"):
#         results = modules["indexer"].smart_search(query, 8)
#         if results:
#             return {
#                 "type": "file_results",
#                 "text": f"I found {len(results)} file(s) related to \"{query}\":",
#                 "data": results,
#             }

#     # Generic fallback
#     return {
#         "type": "chat",
#         "text": (
#             f"I'm not sure what you mean by \"{message}\". Here are some things I can help with:\n\n"
#             "• **Find files** — \"Where is my resume?\"\n"
#             "• **Search by content** — \"Find files about budget\"\n"
#             "• **System status** — \"How is my system?\"\n"
#             "• **Security scan** — \"Scan for threats\"\n"
#             "• **Find duplicates** — \"Find duplicate files\"\n\n"
#             "Type **help** to see all commands."
#         ),
#         "data": None,
#     }


# # ─── Response builders ────────────────────────────────────────────────────────

# def _greeting() -> str:
#     h = datetime.datetime.now().hour
#     if   h < 12: t = "Good morning"
#     elif h < 17: t = "Good afternoon"
#     else:         t = "Good evening"
#     return (
#         f"{t}! I'm ARIA, your local OS assistant.\n\n"
#         "I can help you **find files**, **monitor your system**, "
#         "**run security scans**, and more — all 100% offline.\n\n"
#         "What would you like to do?"
#     )


# def _help_response() -> Dict:
#     return {
#         "type": "help",
#         "text": "Here's everything I can do:",
#         "data": {
#             "commands": [
#                 ("🔍", "Find file by name", "\"Where is my resume?\" or \"Find file report.pdf\""),
#                 ("📄", "Search by content",  "\"Find files about budget 2024\""),
#                 ("🕑", "Recent files",        "\"Show recent files\""),
#                 ("📦", "Find duplicates",     "\"Find duplicate files\" or \"Free up disk space\""),
#                 ("💻", "System status",       "\"How is my system?\" or \"Check CPU usage\""),
#                 ("⚙",  "Running processes",   "\"What processes are running?\""),
#                 ("🔐", "Security scan",       "\"Scan for threats\" or \"Check security\""),
#                 ("❓", "Help",                "\"Help\" or \"What can you do?\""),
#             ]
#         },
#     }


# def _file_search(query: str, intent: str, modules: Dict) -> Dict:
#     if not query or len(query) < 2:
#         return {"type":"chat","text":"What file are you looking for? Please give me a name or description.","data":None}

#     indexer = modules["indexer"]
#     stats   = indexer.get_stats()

#     if stats["total_files"] == 0:
#         return {
#             "type": "chat",
#             "text": (
#                 "⚠️ Your files haven't been indexed yet.\n\n"
#                 "Click **Index Files** in the sidebar or go to **Settings → Indexing** to index your drive first. "
#                 "It only takes a minute and runs in the background."
#             ),
#             "data": None,
#         }

#     if intent == "file_content":
#         results = indexer.content_search(query, 12)
#         label = f"content related to \"{query}\""
#     else:
#         results = indexer.smart_search(query, 12)
#         label = f"\"{query}\""

#     if not results:
#         # Suggest alternatives
#         words  = query.split()
#         alt    = []
#         for w in words[:3]:
#             if len(w) > 3:
#                 r = indexer.name_search(w, 3)
#                 alt.extend(r)
#         if alt:
#             return {
#                 "type": "file_results",
#                 "text": f"No exact match for {label}. Here are some similar files:",
#                 "data": alt,
#             }
#         return {
#             "type": "chat",
#             "text": (
#                 f"No files found matching {label}.\n\n"
#                 f"The index currently has **{stats['total_files']:,} files**. "
#                 "Try different keywords, or make sure the file is in an indexed folder."
#             ),
#             "data": None,
#         }

#     return {
#         "type": "file_results",
#         "text": f"Found **{len(results)}** file(s) matching {label}:",
#         "data": results,
#     }


# def _recent_files(modules: Dict) -> Dict:
#     results = modules["indexer"].recent_files(10)
#     if not results:
#         return {"type":"chat","text":"No recent files found. Index your drive first.","data":None}
#     return {"type":"file_results","text":f"Here are your {len(results)} most recently modified files:","data":results}


# def _duplicates(modules: Dict) -> Dict:
#     stats = modules["indexer"].get_stats()
#     if stats["total_files"] == 0:
#         return {"type":"chat","text":"Index your files first before scanning for duplicates.","data":None}
#     dupes = modules["indexer"].find_duplicates()
#     total_mb = sum(d["wasted_mb"] for d in dupes)
#     if not dupes:
#         return {"type":"chat","text":"✅ Great news — no duplicate files found!","data":None}
#     return {
#         "type": "duplicates",
#         "text": f"Found **{len(dupes)}** duplicate group(s) — you can recover **{total_mb:.1f} MB**:",
#         "data": dupes,
#     }


# def _system_status(modules: Dict) -> Dict:
#     data   = modules["monitor"].get_status()
#     cpu    = data["cpu"]["percent"]
#     ram    = data["memory"]["percent"]
#     disks  = data["disk"]
#     score  = data["health_score"]
#     alerts = data["alerts"]
#     bat    = data["battery"]
#     sys    = data["system"]

#     lines = [
#         f"**System Health: {score}/100** — {sys['os']} · {sys['hostname']} · Uptime {sys['uptime']}",
#         "",
#         f"• CPU: **{cpu:.0f}%** ({data['cpu']['cores_physical']} physical cores)",
#         f"• RAM: **{data['memory']['used_gb']:.1f} GB** used of {data['memory']['total_gb']:.1f} GB ({ram:.0f}%)",
#     ]
#     for d in disks[:2]:
#         lines.append(f"• Disk `{d['mountpoint']}`: **{d['used_gb']:.1f} GB** used of {d['total_gb']:.1f} GB ({d['percent']:.0f}%)")
#     if bat:
#         bat_status = "🔌 Charging" if bat['plugged'] else f"⚡ {bat['time_left']} remaining"
#         lines.append(f"• Battery: **{bat['percent']:.0f}%** {bat_status}")
#     if alerts:
#         lines.append("")
#         lines.append("**Alerts:**")
#         for a in alerts:
#             lines.append(f"• {'⚠️' if a['level']=='warning' else '🔴'} {a['message']}")

#     return {
#         "type": "system_status",
#         "text": "\n".join(lines),
#         "data": data,
#     }


# def _processes(modules: Dict) -> Dict:
#     data  = modules["monitor"].get_status()
#     procs = data["top_processes"]
#     lines = [f"**Top Processes by CPU Usage:**", ""]
#     for p in procs:
#         bar = "█" * int(p['cpu'] / 10)
#         lines.append(f"• **{p['name']}** (PID {p['pid']}) — CPU: {p['cpu']:.1f}% | RAM: {p['mem']:.1f}%")
#     return {"type":"chat","text":"\n".join(lines),"data":None}


# def _security(modules: Dict) -> Dict:
#     data = modules["security"].quick_scan()
#     return {
#         "type": "security_report",
#         "text": f"**Security Scan Complete** — Risk Score: {data['risk_score']}/100\n\n{data['summary']}",
#         "data": data,
#     }

# Version 1.0.2
"""
ARIA Intent Engine — Accurate, direct responses to every query.
Each intent maps to a specific module and returns structured data.
"""
import re, os, datetime
from pathlib import Path
from typing import Dict, Optional, List


# ─── Intent pattern map ───────────────────────────────────────────────────────
INTENTS = {
    "file_name": [
        r"\bwhere is\b", r"\bwhere('s| is) my\b",
        r"\bfind file\b", r"\bfind my file\b",
        r"\blocate\b", r"\bsearch for file\b",
        r"\blook for\b", r"\bget file\b",
        r"\bwhich folder\b", r"\bin which\b.*file",
        r"\bfile called\b", r"\bfile named\b",
        r"\bfind.*\.pdf\b", r"\bfind.*\.docx\b",
        r"\bfind.*\.xlsx\b", r"\bfind.*\.txt\b",
        r"\bfind.*\.py\b", r"\bfind.*\.\w{2,4}\b",
    ],
    "file_content": [
        r"\bfile (about|containing|related to|with content)\b",
        r"\bdocument about\b", r"\bfiles? about\b",
        r"\bfind content\b", r"\bsearch content\b",
        r"\brelated to\b.*\bfile\b",
        r"\bfile.*mentions\b", r"\bfile.*has\b.*word",
    ],
    "file_recent": [
        r"\brecent files?\b", r"\blast.*files?\b",
        r"\blatest files?\b", r"\bfiles? i (worked|opened|used|modified|edited|accessed) recently\b",
        r"\bwhat.*files? did i\b", r"\brecently modified\b",
    ],
    "duplicates": [
        r"\bduplicate\b", r"\bsame files?\b",
        r"\bidentical files?\b", r"\bredundant files?\b",
        r"\bfree.*space\b", r"\bclean.*disk\b",
        r"\bwasted.*space\b", r"\bclean up\b",
        r"\bdelete.*copies?\b",
    ],
    "system": [
        r"\bsystem (status|info|health|performance|stats?|check|overview)\b",
        r"\bhow is my (system|pc|computer|machine|laptop)\b",
        r"\bcpu (usage|status|load|percent)\b",
        r"\bram (usage|status|percent)\b",
        r"\bmemory (usage|status|percent)\b",
        r"\bdisk (usage|space|status)\b",
        r"\bbattery (status|level|percent)\b",
        r"\buptime\b", r"\bsystem info\b",
        r"\bwhat.*running\b", r"\bcheck (my )?(system|computer|pc)\b",
        r"\bprocessor\b", r"\btemperature\b",
    ],
    "processes": [
        r"\b(running )?processes?\b", r"\btask manager\b",
        r"\btop processes?\b", r"\bwhat.*process(es)?\b",
        r"\bwhich apps?\b", r"\bopen apps?\b",
        r"\bbackground.*running\b",
    ],
    "disk_space": [
        r"\bdisk space\b", r"\bstorage space\b",
        r"\bhow much.*space\b", r"\bfree space\b",
        r"\bstorage left\b",
    ],
    "network": [
        r"\bnetwork\b", r"\binternet\b", r"\bconnection\b",
        r"\bip address\b", r"\bwifi\b", r"\bopen ports?\b",
        r"\blistening ports?\b",
    ],
    "security": [
        r"\bsecurity (scan|check|status|report)\b",
        r"\bscan (for )?(threats?|viruses?|malware)\b",
        r"\bcheck.*(threats?|viruses?|malware|security)\b",
        r"\bmalware\b", r"\bvirus\b", r"\bhack\b",
        r"\bsuspicious (process|activity|file)\b",
        r"\bis.*safe\b", r"\bsecurity\b",
        r"\bfirewall\b", r"\bintrusion\b", r"\bransomware\b",
    ],
    "open_file": [
        r"\bopen (the |this |my )?\w.*\.(pdf|docx?|xlsx?|txt|py|js|png|jpg)\b",
        r"\blaunch (the |this )?\w",
    ],
    "greeting": [
        r"^(hi|hello|hey|good (morning|afternoon|evening)|howdy|greetings?|what'?s up)[!.,? ]*$",
    ],
    "thanks": [
        r"^(thanks?|thank you|thx|ty|great|nice|awesome|perfect|cool|good job)[!.,? ]*$",
    ],
    "help": [
        r"\bhelp\b", r"\bwhat can you\b",
        r"\bcommands?\b", r"\bfeatures?\b",
        r"\bcapabilit(y|ies)\b",
        r"\bhow (do i|to) use\b",
        r"\bwhat (do|can) you\b",
    ],
}


# Priority order — more specific intents checked before broader ones
_PRIORITY = [
    "greeting", "thanks", "help",
    "file_recent", "file_content", "file_name",
    "duplicates", "processes", "disk_space", "security", "network", "system", "open_file",
]

def detect_intent(text: str) -> Optional[str]:
    t = text.lower().strip()
    for intent in _PRIORITY:
        for pat in INTENTS.get(intent, []):
            if re.search(pat, t):
                return intent
    return None


def extract_query(text: str) -> str:
    """Pull the core subject from the user's message."""
    t = text.strip()
    # Remove common question prefixes
    strip = [
        r"^(can you |could you |please |aria[,\s]+)",
        r"^(find|locate|search for|where is|where'?s|look for|get|show me|give me|tell me|list)\s+(the\s+|my\s+|a\s+)?",
        r"^(file(s)? about|file(s)? containing|file(s)? related to|file(s)? named|files? called|document about)\s+",
        r"\?$", r"\.$", r"!$",
    ]
    for pat in strip:
        t = re.sub(pat, '', t, flags=re.IGNORECASE).strip()
    return t.strip() or text.strip()


def build_response(message: str, modules: Dict) -> Dict:
    """Main dispatcher. Always returns a precise, structured response."""
    intent = detect_intent(message)
    query  = extract_query(message)

    # Direct intent routing
    if intent == "greeting":
        return _greeting()

    if intent == "thanks":
        return {"type": "chat", "text": "You're welcome! Let me know if there's anything else I can help with.", "data": None}

    if intent == "help":
        return _help()

    if intent in ("file_name", "file_content"):
        return _file_search(query, intent, modules)

    if intent == "file_recent":
        return _recent_files(modules)

    if intent == "duplicates":
        return _duplicates(modules)

    if intent in ("system", "disk_space", "network"):
        return _system_status(modules)

    if intent == "processes":
        return _processes(modules)

    if intent == "security":
        return _security(modules)

    # Fallback: try smart file search if query looks meaningful
    q = query.strip()
    if len(q) >= 2 and not q.startswith("-"):
        indexer = modules.get("indexer")
        if indexer:
            stats = indexer.get_stats()
            if stats["total_files"] > 0:
                results = indexer.smart_search(q, 10)
                if results:
                    return {
                        "type": "file_results",
                        "text": f"Found **{len(results)}** file(s) matching \"{q}\":",
                        "data": results,
                    }

    return _unknown(message)


# ─── Response builders ────────────────────────────────────────────────────────

def _greeting() -> Dict:
    h = datetime.datetime.now().hour
    t = "Good morning" if h < 12 else ("Good afternoon" if h < 17 else "Good evening")
    return {
        "type": "chat",
        "text": (
            f"{t}! I'm **ARIA**, your local OS assistant. 👋\n\n"
            "I can help you:\n"
            "• **Find files** by name or content\n"
            "• **Monitor your system** — CPU, RAM, disk, battery\n"
            "• **Run security scans** — threats, ports, processes\n"
            "• **Find duplicate files** and recover disk space\n\n"
            "What would you like to do?"
        ),
        "data": None,
    }


def _help() -> Dict:
    return {
        "type": "help",
        "text": "Here's everything I can do — click any card to try it:",
        "data": {
            "commands": [
                ("🔍", "Find file by name",   "\"Where is my resume?\""),
                ("📄", "Search by content",   "\"Find files about budget 2024\""),
                ("🕑", "Recent files",         "\"Show recent files\""),
                ("📦", "Find duplicates",      "\"Find duplicate files\""),
                ("💻", "System status",        "\"How is my system?\""),
                ("⚙",  "Running processes",    "\"What processes are running?\""),
                ("🔐", "Security scan",        "\"Scan for threats\""),
                ("🌐", "Network info",         "\"Show network status\""),
            ]
        },
    }


def _file_search(query: str, intent: str, modules: Dict) -> Dict:
    q = query.strip()
    if not q or len(q) < 2:
        return {
            "type": "chat",
            "text": "What file are you looking for? Please give me a filename or describe its contents.",
            "data": None,
        }

    indexer = modules.get("indexer")
    if not indexer:
        return {"type": "chat", "text": "File indexer unavailable.", "data": None}

    stats = indexer.get_stats()
    if stats["total_files"] == 0:
        return {
            "type": "chat",
            "text": (
                "⚠️ **Files not indexed yet.**\n\n"
                "Click **⚡ Index Files** in the header, or use **Settings → Indexing** to choose folders.\n"
                "Indexing runs in the background and usually takes 1–3 minutes."
            ),
            "data": None,
        }

    if intent == "file_content":
        results = indexer.content_search(q, 12)
        label   = f"content related to \"{q}\""
    else:
        results = indexer.smart_search(q, 12)
        label   = f"\"{q}\""

    if results:
        return {
            "type": "file_results",
            "text": f"Found **{len(results)}** file(s) matching {label}:",
            "data": results,
        }

    # Try progressively shorter sub-queries
    words = [w for w in q.split() if len(w) >= 3]
    alt = []
    for w in words[:3]:
        r = indexer.name_search(w, 4)
        for item in r:
            if item["path"] not in {a["path"] for a in alt}:
                alt.append(item)

    if alt:
        return {
            "type": "file_results",
            "text": (
                f"No exact match for {label}.\n"
                f"Here are the closest files I found  ({stats['total_files']:,} files indexed):"
            ),
            "data": alt,
        }

    return {
        "type": "chat",
        "text": (
            f"No files found matching {label}.\n\n"
            f"The index has **{stats['total_files']:,} files**. "
            "Try different keywords, check if the file is in an indexed folder, "
            "or click **⚡ Index Files** to refresh the index."
        ),
        "data": None,
    }


def _recent_files(modules: Dict) -> Dict:
    indexer = modules.get("indexer")
    if not indexer or indexer.get_stats()["total_files"] == 0:
        return {"type": "chat", "text": "Index your files first — click **⚡ Index Files**.", "data": None}
    results = indexer.recent_files(12)
    if not results:
        return {"type": "chat", "text": "No recent files found.", "data": None}
    return {
        "type": "file_results",
        "text": f"Here are your **{len(results)} most recently modified** files:",
        "data": results,
    }


def _duplicates(modules: Dict) -> Dict:
    indexer = modules.get("indexer")
    if not indexer:
        return {"type": "chat", "text": "Indexer unavailable.", "data": None}
    stats = indexer.get_stats()
    if stats["total_files"] == 0:
        return {"type": "chat", "text": "Index your files first — click **⚡ Index Files**.", "data": None}

    groups = indexer.find_duplicates(limit=30)
    if not groups:
        return {
            "type": "chat",
            "text": (
                f"✅ **No duplicate files found!**\n\n"
                f"Scanned **{stats['total_files']:,} files** — your disk is clean."
            ),
            "data": None,
        }

    total_mb  = sum(g.get("wasted_mb", 0) for g in groups)
    total_files = sum(g.get("count", 0) for g in groups)
    return {
        "type": "duplicates",
        "text": (
            f"Found **{len(groups)} duplicate group(s)** across **{total_files} files**. "
            f"You can recover up to **{total_mb:.1f} MB** by removing the extras:"
        ),
        "data": groups,
    }


def _system_status(modules: Dict) -> Dict:
    monitor = modules.get("monitor")
    if not monitor:
        return {"type": "chat", "text": "System monitor unavailable.", "data": None}

    data   = monitor.get_status()
    cpu    = data.get("cpu", {})
    mem    = data.get("memory", {})
    disks  = data.get("disk", []) or []
    bat    = data.get("battery")
    sys_   = data.get("system", {})
    score  = data.get("health_score", 100)
    alerts = data.get("alerts", [])

    sc = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 50 else "Poor"

    lines = [
        f"**System Health: {score}/100** ({sc})",
        f"OS: {sys_.get('os', '?')} · Host: {sys_.get('hostname', '?')} · Uptime: {sys_.get('uptime', '?')}",
        "",
        f"• **CPU:** {cpu.get('percent', 0):.1f}% load  —  {cpu.get('cores_physical', '?')} physical cores",
        f"• **RAM:** {mem.get('used_gb', 0):.2f} GB used / {mem.get('total_gb', 0):.1f} GB total  ({mem.get('percent', 0):.1f}%)",
    ]
    for d in disks[:2]:
        lines.append(
            f"• **Disk** `{d.get('mountpoint', '?')}`:  "
            f"{d.get('used_gb', 0):.1f} GB used / {d.get('total_gb', 0):.1f} GB  "
            f"({d.get('percent', 0):.1f}%  —  {d.get('free_gb', 0):.1f} GB free)"
        )
    if bat:
        plug = "Charging 🔌" if bat.get("plugged") else f"{bat.get('time_left', '?')} remaining"
        lines.append(f"• **Battery:** {bat.get('percent', 0):.1f}%  —  {plug}")

    if alerts:
        lines.append("")
        lines.append("**⚠ Alerts:**")
        for a in alerts:
            lines.append(f"• {a.get('message', '')}")

    return {
        "type": "system_status",
        "text": "\n".join(lines),
        "data": data,
    }


def _processes(modules: Dict) -> Dict:
    monitor = modules.get("monitor")
    if not monitor:
        return {"type": "chat", "text": "System monitor unavailable.", "data": None}

    data  = monitor.get_status()
    procs = data.get("top_processes", [])

    # Return as system_status so the SystemCard renders the process table
    return {
        "type": "system_status",
        "text": f"Here are the **top {len(procs)} processes** by CPU usage right now:",
        "data": data,
    }


def _security(modules: Dict) -> Dict:
    sec = modules.get("security")
    if not sec:
        return {"type": "chat", "text": "Security scanner unavailable.", "data": None}

    data  = sec.quick_scan()
    risk  = data.get("risk_score", 0)
    procs = data.get("suspicious_processes", [])
    ports = data.get("open_ports", [])
    integ = data.get("integrity_changes", [])
    usb   = data.get("usb_devices", [])
    susp_ports = [p for p in ports if p.get("suspicious")]

    lines = [f"**Security Scan Complete** — Risk Score: **{risk}/100**", ""]

    if risk == 0:
        lines.append("✅ **All clear!** No threats detected. Your system appears clean.")
    else:
        if procs:
            lines.append(f"🔴 **{len(procs)} suspicious process(es)** detected")
        if integ:
            lines.append(f"🔴 **{len(integ)} critical system file(s)** have been modified")
        if susp_ports:
            lines.append(f"⚠️ **{len(susp_ports)} suspicious port(s)** are open")
        if usb:
            lines.append(f"🔌 **{len(usb)} USB device(s)** connected")

    lines += [
        "",
        f"• Ports monitored: **{len(ports)}**",
        f"• USB devices: **{len(usb)}**",
        f"• Integrity changes: **{len(integ)}**",
        f"• Failed logins: **{len(data.get('failed_logins', []))}**",
    ]

    return {
        "type": "security_report",
        "text": "\n".join(lines),
        "data": data,
    }


def _unknown(message: str) -> Dict:
    return {
        "type": "chat",
        "text": (
            f"I'm not sure how to handle: \"{message}\"\n\n"
            "Here's what I can do:\n"
            "• **Find file** — \"Where is my resume?\"\n"
            "• **Search content** — \"Find files about budget\"\n"
            "• **System status** — \"How is my system?\"\n"
            "• **Security scan** — \"Scan for threats\"\n"
            "• **Duplicates** — \"Find duplicate files\"\n"
            "• **Recent files** — \"Show recent files\"\n\n"
            "Type **help** to see all commands with examples."
        ),
        "data": None,
    }