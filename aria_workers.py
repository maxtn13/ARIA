"""
ARIA Workers — QThread-based background tasks
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtCore import QThread, pyqtSignal
from core.intent_engine import build_response


class IndexWorker(QThread):
    """Indexes a directory in the background."""
    progress = pyqtSignal(int, int)       # done, total
    status   = pyqtSignal(str)            # status message
    finished = pyqtSignal(int)            # total indexed

    def __init__(self, path: str, indexer):
        super().__init__()
        self.path    = path
        self.indexer = indexer
        self._abort  = False

    def run(self):
        count = self.indexer.index_directory(
            self.path,
            progress_cb = lambda d, t: self.progress.emit(d, t),
            status_cb   = lambda msg: self.status.emit(msg),
        )
        self.finished.emit(count)

    def abort(self):
        self._abort = True


class ChatWorker(QThread):
    """Processes a chat message in the background."""
    response = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, message: str, modules: dict):
        super().__init__()
        self.message = message
        self.modules = modules

    def run(self):
        try:
            # First try local intent engine (always fast)
            result = build_response(self.message, self.modules)

            # If result has no useful data, try Ollama for richer response
            if result.get("type") == "chat" and self.modules.get("ollama_available"):
                ollama_resp = self._ask_ollama(self.message)
                if ollama_resp:
                    result["text"] = ollama_resp

            self.response.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _ask_ollama(self, message: str) -> str:
        try:
            import urllib.request, json as _json
            from aria_config import config
            url   = config.get("ollama_url") + "/api/chat"
            model = config.get("ollama_model")
            body  = _json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": (
                        "You are ARIA, a local OS assistant. Be concise and helpful. "
                        "Answer questions about files, system performance, and computing. "
                        "You run entirely offline on the user's machine."
                    )},
                    {"role": "user", "content": message}
                ],
                "stream": False
            }).encode()
            req = urllib.request.Request(url, data=body,
                                         headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = _json.loads(r.read())
                return data.get("message", {}).get("content", "")
        except Exception:
            return ""


class StatsWorker(QThread):
    """Polls system stats every N seconds."""
    stats = pyqtSignal(dict)

    def __init__(self, interval_ms: int = 4000):
        super().__init__()
        self.interval = interval_ms
        self._running = True

    def run(self):
        from core.system_security import SystemMonitor
        mon = SystemMonitor()
        while self._running:
            try:
                self.stats.emit(mon.get_status())
            except Exception:
                pass
            self.msleep(self.interval)

    def stop(self):
        self._running = False
