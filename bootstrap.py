import sys
import os
import subprocess
import importlib
import threading
import tkinter as tk
from tkinter import ttk

DEPENDANCES = [
    ("cryptography",  "cryptography",  "41.0.0",  True),
    ("watchdog",      "watchdog",      "3.0.0",   True),
    ("pystray",       "pystray",       "0.19.0",  True),
    ("PIL",           "Pillow",        "10.0.0",  True),
    ("win32api",      "pywin32",       "306",     True),
    ("requests",      "requests",      "2.31.0",  False),
    ("psutil",        "psutil",        "5.9.0",   False),
    ("packaging",     "packaging",     "23.0",    False),
]

def mettre_a_jour_pip():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
        capture_output=True, timeout=30
    )

def installer(nom_pip, version_min=None):
    cible = f"{nom_pip}>={version_min}" if version_min else nom_pip
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", cible, "--quiet"],
        capture_output=True, timeout=120
    )
    return r.returncode == 0

def verifier(nom_import):
    try:
        importlib.import_module(nom_import)
        return True
    except ImportError:
        return False

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brother Scan Center")
        self.geometry("520x400")
        self.resizable(False, False)
        self.configure(bg="#003087")
        self.overrideredirect(True)
        self.succes = False
        self._centrer()
        self._build()
        self.after(500, self._lancer)

    def _centrer(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 520) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"520x400+{x}+{y}")

    def _build(self):
        tk.Label(
            self,
            text="Brother Scan Center",
            font=("Segoe UI", 18, "bold"),
            bg="#003087",
            fg="white"
        ).pack(pady=(30, 5))

        tk.Label(
            self,
            text="DCP-9020CDW",
            font=("Segoe UI", 10),
            bg="#003087",
            fg="#a0c4ff"
        ).pack()

        self.card = tk.Frame(self, bg="#f0f4f8", padx=15, pady=10)
        self.card.pack(fill="x", padx=25, pady=15)

        self.status = tk.Label(
            self.card,
            text="Initialisation...",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8",
            fg="#003087"
        )
        self.status.pack(anchor="w")

        self.detail = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 9),
            bg="#f0f4f8",
            fg="#555"
        )
        self.detail.pack(anchor="w")

        self.bar = ttk.Progressbar(
            self.card,
            mode="determinate",
            length=460
        )
        self.bar.pack(fill="x", pady=5)

        self.log = tk.Text(
            self.card,
            height=7,
            font=("Consolas", 8),
            bg="#1e1e1e",
            fg="#00ff00",
            relief="flat",
            state="disabled"
        )
        self.log.pack(fill="x")

        tk.Label(
            self,
            text="v1.0.0",
            font=("Segoe UI", 8),
            bg="#003087",
            fg="#6c9fd4"
        ).pack(side="bottom", pady=5)

    def ajouter_log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", f"  {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")
        self.update()

    def set_status(self, t, d=""):
        self.status.config(text=t)
        self.detail.config(text=d)
        self.update()

    def _lancer(self):
        threading.Thread(target=self._verifier, daemon=True).start()

    def _verifier(self):
        total = len(DEPENDANCES) + 2
        etape = 0
        erreurs = []

        self.set_status("Mise a jour pip...")
        mettre_a_jour_pip()
        self.ajouter_log("pip a jour")
        etape += 1
        self.bar["value"] = int(etape / total * 100)

        installer("packaging")
        etape += 1
        self.bar["value"] = int(etape / total * 100)

        for nom_import, nom_pip, version_min, critique in DEPENDANCES:
            self.set_status(f"Verification {nom_pip}...")
            if verifier(nom_import):
                self.ajouter_log(f"OK {nom_pip}")
            else:
                self.ajouter_log(f"Installation {nom_pip}...")
                ok = installer(nom_pip, version_min)
                if ok:
                    self.ajouter_log(f"OK {nom_pip} installe")
                else:
                    self.ajouter_log(f"ERREUR {nom_pip}")
                    if critique:
                        erreurs.append(nom_pip)
            etape += 1
            self.bar["value"] = int(etape / total * 100)

        self.bar["value"] = 100

        if erreurs:
            self.set_status(
                "Erreurs installation",
                ", ".join(erreurs)
            )
            self.after(3000, self.destroy)
        else:
            self.set_status("Tout est pret !", "Lancement...")
            self.succes = True
            self.after(1500, self.destroy)
