"""
ARIA System Monitor + Security Scanner
"""
import os, psutil, platform, datetime, hashlib, socket
from typing import Dict, List, Optional

SUSPICIOUS_PROCS = {'keylogger','xmrig','minerd','cpuminer','nanominer','cgminer','cryptominer'}
SUSPICIOUS_PORTS = {1337,31337,4444,5555,6666,6667,7777,9999,12345,54321,65535}
CRITICAL_FILES   = ['/etc/passwd','/etc/shadow','/etc/hosts','/etc/sudoers','/etc/ssh/sshd_config']


# ─── SYSTEM MONITOR ──────────────────────────────────────────────────────────

class SystemMonitor:
    def get_status(self) -> Dict:
        cpu   = self._cpu()
        mem   = self._mem()
        disks = self._disks()
        net   = self._net()
        bat   = self._battery()
        procs = self._top_procs()
        sys   = self._sysinfo()
        score = self._health_score(cpu, mem, disks)
        alerts = self._alerts(cpu, mem, disks, bat)
        return dict(cpu=cpu, memory=mem, disk=disks, network=net, battery=bat,
                    top_processes=procs, system=sys, health_score=score,
                    alerts=alerts, timestamp=datetime.datetime.now().isoformat())

    def _cpu(self):
        freq = psutil.cpu_freq()
        per  = psutil.cpu_percent(interval=0.3)
        temps = {}
        try:
            t = psutil.sensors_temperatures()
            if t:
                for name, entries in t.items():
                    if entries:
                        temps[name] = round(entries[0].current, 1)
        except Exception:
            pass
        return {
            "percent": per,
            "cores_physical": psutil.cpu_count(logical=False) or 1,
            "cores_logical":  psutil.cpu_count(logical=True) or 1,
            "frequency_mhz":  round(freq.current) if freq else None,
            "per_core":       psutil.cpu_percent(percpu=True, interval=0.1),
            "temperatures":   temps,
        }

    def _mem(self):
        m = psutil.virtual_memory()
        s = psutil.swap_memory()
        return {
            "total_gb":     round(m.total   / 2**30, 2),
            "used_gb":      round(m.used    / 2**30, 2),
            "available_gb": round(m.available / 2**30, 2),
            "percent":      m.percent,
            "swap_gb":      round(s.used    / 2**30, 2),
            "swap_percent": s.percent,
        }

    def _disks(self):
        result = []
        for p in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(p.mountpoint)
                result.append({
                    "device":    p.device,
                    "mountpoint":p.mountpoint,
                    "total_gb":  round(u.total / 2**30, 2),
                    "used_gb":   round(u.used  / 2**30, 2),
                    "free_gb":   round(u.free  / 2**30, 2),
                    "percent":   u.percent,
                })
            except Exception:
                pass
        return result

    def _net(self):
        s = psutil.net_io_counters()
        conns = psutil.net_connections()
        return {
            "bytes_sent_mb": round(s.bytes_sent / 2**20, 1),
            "bytes_recv_mb": round(s.bytes_recv / 2**20, 1),
            "established":   sum(1 for c in conns if c.status == 'ESTABLISHED'),
            "listening_ports": sorted({c.laddr.port for c in conns if c.status=='LISTEN' and c.laddr})[:20],
        }

    def _battery(self):
        b = psutil.sensors_battery()
        if not b: return None
        sec = b.secsleft
        return {
            "percent": round(b.percent, 1),
            "plugged": b.power_plugged,
            "time_left": (
                f"{sec//3600}h {(sec%3600)//60}m" if sec > 0 and not b.power_plugged
                else ("Charging" if b.power_plugged else "N/A")
            )
        }

    def _top_procs(self, n=8):
        procs = []
        for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent','status']):
            try:
                i = p.info
                procs.append({"pid":i['pid'],"name":i['name'],
                              "cpu":round(i['cpu_percent'] or 0,1),
                              "mem":round(i['memory_percent'] or 0,1)})
            except Exception:
                pass
        return sorted(procs, key=lambda x: x['cpu'], reverse=True)[:n]

    def _sysinfo(self):
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        up   = datetime.datetime.now() - boot
        h, r = divmod(int(up.total_seconds()), 3600)
        return {
            "os":        platform.system(),
            "version":   platform.version()[:60],
            "hostname":  platform.node(),
            "arch":      platform.machine(),
            "uptime":    f"{h}h {r//60}m",
            "boot_time": boot.strftime("%Y-%m-%d %H:%M"),
            "python":    platform.python_version(),
        }

    def _health_score(self, cpu, mem, disks) -> int:
        score = 100
        c = cpu['percent']
        m = mem['percent']
        d = max((dk['percent'] for dk in disks), default=0)
        if c > 90: score -= 30
        elif c > 70: score -= 12
        elif c > 50: score -= 4
        if m > 90: score -= 30
        elif m > 75: score -= 12
        elif m > 55: score -= 4
        if d > 95: score -= 30
        elif d > 85: score -= 10
        return max(0, score)

    def _alerts(self, cpu, mem, disks, bat) -> List[Dict]:
        alerts = []
        if cpu['percent'] > 85:
            alerts.append({"level":"warning","type":"cpu","message":f"High CPU usage: {cpu['percent']:.0f}%"})
        if mem['percent'] > 85:
            alerts.append({"level":"warning","type":"memory","message":f"High RAM: {mem['percent']:.0f}% used"})
        for d in disks:
            if d['percent'] > 90:
                alerts.append({"level":"critical","type":"disk","message":f"Disk almost full: {d['mountpoint']} at {d['percent']:.0f}%"})
        if bat and not bat['plugged'] and bat['percent'] < 15:
            alerts.append({"level":"critical","type":"battery","message":f"Low battery: {bat['percent']:.0f}%"})
        return alerts


# ─── SECURITY SCANNER ────────────────────────────────────────────────────────

class SecurityScanner:
    def __init__(self):
        self._baseline: Dict[str,str] = {}
        self._build_baseline()

    def quick_scan(self) -> Dict:
        susp_procs  = self._scan_processes()
        open_ports  = self._scan_ports()
        integrity   = self._check_integrity()
        usb         = self._usb_devices()
        failed_logins = self._failed_logins()
        risk = self._risk_score(susp_procs, open_ports, integrity)
        return {
            "timestamp":            datetime.datetime.now().isoformat(),
            "suspicious_processes": susp_procs,
            "open_ports":           open_ports,
            "integrity_changes":    integrity,
            "usb_devices":          usb,
            "failed_logins":        failed_logins,
            "risk_score":           risk,
            "summary":              self._summary(risk, susp_procs, integrity),
        }

    def _build_baseline(self):
        for fp in CRITICAL_FILES:
            try:
                h = hashlib.sha256()
                with open(fp,'rb') as f: h.update(f.read())
                self._baseline[fp] = h.hexdigest()
            except Exception:
                pass

    def _scan_processes(self):
        found = []
        for p in psutil.process_iter(['pid','name','exe']):
            try:
                n = (p.info['name'] or '').lower()
                if any(s in n for s in SUSPICIOUS_PROCS):
                    found.append({"pid":p.info['pid'],"name":p.info['name'],"exe":p.info.get('exe','?')})
            except Exception:
                pass
        return found

    def _scan_ports(self):
        ports = []
        try:
            for c in psutil.net_connections(kind='inet'):
                if c.status == 'LISTEN' and c.laddr:
                    pname = '?'
                    try:
                        if c.pid: pname = psutil.Process(c.pid).name()
                    except Exception:
                        pass
                    ports.append({
                        "port":c.laddr.port,"process":pname,"pid":c.pid,
                        "suspicious": c.laddr.port in SUSPICIOUS_PORTS,
                    })
        except Exception:
            pass
        return sorted(ports, key=lambda x: x['suspicious'], reverse=True)

    def _check_integrity(self):
        changes = []
        for fp, orig in self._baseline.items():
            try:
                h = hashlib.sha256()
                with open(fp,'rb') as f: h.update(f.read())
                if h.hexdigest() != orig:
                    changes.append({"file":fp,"status":"MODIFIED","severity":"high"})
            except Exception:
                pass
        return changes

    def _usb_devices(self):
        devs = []
        for p in psutil.disk_partitions():
            if 'removable' in p.opts.lower() or 'usb' in p.fstype.lower():
                try:
                    u = psutil.disk_usage(p.mountpoint)
                    devs.append({"device":p.device,"mountpoint":p.mountpoint,
                                 "size_gb":round(u.total/2**30,2)})
                except Exception:
                    pass
        return devs

    def _failed_logins(self, max_lines=10):
        for lp in ['/var/log/auth.log','/var/log/secure']:
            if os.path.exists(lp):
                try:
                    with open(lp,'r',errors='ignore') as f:
                        lines = f.readlines()
                    return [l.strip() for l in lines if 'Failed password' in l][-max_lines:]
                except Exception:
                    pass
        return []

    def _risk_score(self, procs, ports, integrity) -> int:
        risk = 0
        risk += len(procs) * 25
        risk += len(integrity) * 30
        risk += sum(20 for p in ports if p['suspicious'])
        return min(100, risk)

    def _summary(self, risk, procs, integrity) -> str:
        if risk == 0:    return "✅ All clear — no threats detected."
        if risk < 30:    return f"🟡 Low risk. {len(procs)} suspicious process(es), review recommended."
        if risk < 70:    return f"🟠 Moderate risk. Immediate review advised."
        return               f"🔴 HIGH RISK — {len(procs)+len(integrity)} issues detected. Act now."
