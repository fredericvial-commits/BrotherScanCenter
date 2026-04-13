import json, os, base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

CONFIG_PATH = os.path.join(os.environ.get("APPDATA", "."),
    "BrotherScanCenter", "config.json")
KEY_PATH = os.path.join(os.environ.get("APPDATA", "."),
    "BrotherScanCenter", "key.bin")

DEFAULT_CONFIG = {
    "smtp":    {"server": "smtp.gmail.com", "port": 587,
                "email": "", "app_password": ""},
    "scanner": {"ip": "", "model": "DCP-9020CDW",
                "format": "PDF", "resolution": 300},
    "nas":     {"ip": "", "partage": "Scans_Brother",
                "user": "", "password": "", "protocol": "CIFS"},
    "storage": {"scan_folder": "", "archive_folder": "",
                "keep_local": True},
    "email_destinations": [],
    "notifications": {"show_popup": True, "sound": True},
    "app": {"first_run": True, "auto_start": True}
}

class ConfigManager:
    def __init__(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        self.key    = self._get_or_create_key()
        self.fernet = Fernet(self.key)
        self.config = self._charger()

    def _get_or_create_key(self):
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, "rb") as f:
                return f.read()
        machine_id = os.environ.get("COMPUTERNAME", "default").encode()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
            length=32, salt=b"BrotherSC_2024", iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(machine_id))
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        return key

    def _chiffrer(self, v):
        return self.fernet.encrypt(v.encode()).decode()

    def _dechiffrer(self, v):
        try:
            return self.fernet.decrypt(v.encode()).decode()
        except:
            return v

    def _champs_sensibles(self):
        return [("smtp","app_password"), ("nas","password")]

    def _charger(self):
        if not os.path.exists(CONFIG_PATH):
            return dict(DEFAULT_CONFIG)
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        for s, c in self._champs_sensibles():
            try:
                data[s][c] = self._dechiffrer(data[s][c])
            except:
                pass
        return data

    def sauvegarder(self, config):
        self.config = config
        import copy
        data = copy.deepcopy(config)
        for s, c in self._champs_sensibles():
            try:
                if data[s][c]:
                    data[s][c] = self._chiffrer(data[s][c])
            except:
                pass
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def get(self, *keys, default=None):
        d = self.config
        for k in keys:
            if isinstance(d, dict):
                d = d.get(k, {})
            else:
                return default
        return d if d = {} else default

    def set(self, valeur, *keys):
        d = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = valeur
