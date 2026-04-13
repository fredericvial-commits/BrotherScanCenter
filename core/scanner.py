import subprocess, os, logging, json
from datetime import datetime

class BrotherScanner:
    def __init__(self, cfg):
        self.cfg = cfg

    def generer_nom(self):
        ts  = datetime.now().strftime("mHS")
        fmt = self.cfg.get("scanner","format") or "PDF"
        return f"Scan_{ts}.{fmt.lower^(^)}"

    def scanner_document(self):
        dossier = self.cfg.get("storage","scan_folder") or "."
        os.makedirs(dossier, exist_ok=True)
        chemin  = os.path.join(dossier, self.generer_nom())
        res     = self.cfg.get("scanner","resolution") or 300
        script  = f"""
$wia = New-Object -ComObject WIA.DeviceManager
$scanner = $null
foreach ($d in $wia.DeviceInfos) {{
    if ($d.Properties['Name'].Value -like '*Brother*') {{
        $scanner = $d.Connect(); break
    }}
}}
if ($scanner -eq $null) {{ exit 1 }}
$item = $scanner.Items(1)
$item.Properties['6146'].Value = 4
$item.Properties['6147'].Value = {res}
$image = $item.Transfer()
$image.SaveFile('{chemin}')
"""
        r = subprocess.run(
            ["powershell","-Command", script],
            capture_output=True, timeout=60)
        if r.returncode == 0 and os.path.exists(chemin):
            logging.info(f"Scan OK : {chemin}")
            return chemin
        logging.error(f"Scan echoue : {r.stderr}")
        return None
