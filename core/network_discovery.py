import socket
import subprocess
import ipaddress
import logging
from concurrent.futures import ThreadPoolExecutor


class NetworkDiscovery:
    def _get_gateway(self):
        try:
            r = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True
            )
            for line in r.stdout.splitlines():
                if "Passerelle" in line or "Gateway" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ip = parts[-1].strip()
                        if ip:
                            return ip
        except Exception:
            pass
        return "192.168.1.1"

    def scanner_reseau(self, callback_progress=None):
        gateway = self._get_gateway()
        reseau = str(ipaddress.IPv4Network(
            f"{gateway}/24", strict=False
        ))
        ips = [
            str(ip)
            for ip in ipaddress.IPv4Network(reseau).hosts()
        ]
        resultats = []
        total = len(ips)

        with ThreadPoolExecutor(max_workers=50) as ex:
            futures = {
                ex.submit(self._ping_et_identifier, ip): ip
                for ip in ips
            }
            for i, future in enumerate(futures):
                r = future.result()
                if r:
                    resultats.append(r)
                if callback_progress:
                    callback_progress(int(i / total * 100))

        return resultats

    def _ping_et_identifier(self, ip):
        try:
            r = subprocess.run(
                ["ping", "-n", "1", "-w", "500", ip],
                capture_output=True,
                timeout=2
            )
            if r.returncode != 0:
                return None
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = ""
            t = self._identifier_type(ip, hostname)
            if t:
                return {"ip": ip, "hostname": hostname, "type": t}
        except Exception:
            pass
        return None

    def _identifier_type(self, ip, hostname):
        h = hostname.lower()
        if any(x in h for x in ["brother", "brw", "brl"]):
            return "Imprimante Brother"
        if any(x in h for x in ["qnap", "nas", "ts-"]):
            return "NAS QNAP"
        return None
