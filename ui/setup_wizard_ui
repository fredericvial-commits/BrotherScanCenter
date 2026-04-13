import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import smtplib


class SetupWizard(tk.Tk):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.configure_ok = False
        self.etape = 0
        self.vars = {}
        self.etapes = [
            self._bienvenue,
            self._imprimante,
            self._smtp,
            self._nas,
            self._stockage,
            self._fin
        ]
        self.title("Brother Scan Center - Configuration")
        self.geometry("580x480")
        self.resizable(False, False)
        self.configure(bg="#f0f4f8")
        self._centrer()
        self._structure()
        self._afficher()

    def _centrer(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 580) // 2
        y = (self.winfo_screenheight() - 480) // 2
        self.geometry(f"580x480+{x}+{y}")

    def _structure(self):
        self.header = tk.Frame(self, bg="#003087", height=75)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.lbl_titre = tk.Label(
            self.header, text="",
            font=("Segoe UI", 13, "bold"),
            bg="#003087", fg="white"
        )
        self.lbl_titre.pack(side="left", padx=20, pady=20)

        self.lbl_etape = tk.Label(
            self.header, text="",
            font=("Segoe UI", 9),
            bg="#003087", fg="#a0c4ff"
        )
        self.lbl_etape.pack(side="right", padx=20)

        self.content = tk.Frame(self, bg="#f0f4f8")
        self.content.pack(fill="both", expand=True, padx=25, pady=10)

        self.bar = ttk.Progressbar(
            self, mode="determinate",
            maximum=len(self.etapes)
        )
        self.bar.pack(fill="x", padx=25)

        nav = tk.Frame(self, bg="#f0f4f8")
        nav.pack(fill="x", padx=25, pady=10)

        self.btn_retour = tk.Button(
            nav, text="Retour",
            command=self._precedent,
            bg="#6c757d", fg="white",
            relief="flat", padx=15, pady=6
        )
        self.btn_retour.pack(side="left")

        self.btn_suivant = tk.Button(
            nav, text="Suivant",
            command=self._suivant,
            bg="#003087", fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=6
        )
        self.btn_suivant.pack(side="right")

    def _afficher(self):
        for w in self.content.winfo_children():
            w.destroy()
        n = len(self.etapes)
        self.lbl_etape.config(text=f"Etape {self.etape + 1}/{n}")
        self.bar["value"] = self.etape
        self.btn_retour.config(
            state="normal" if self.etape > 0 else "disabled"
        )
        self.btn_suivant.config(
            text="Terminer" if self.etape == n - 1 else "Suivant"
        )
        self.etapes[self.etape]()

    def _suivant(self):
        self._sauvegarder()
        if self.etape < len(self.etapes) - 1:
            self.etape += 1
            self._afficher()
        else:
            self.configure_ok = True
            self.destroy()

    def _precedent(self):
        if self.etape > 0:
            self.etape -= 1
            self._afficher()

    def _field(self, parent, label, cle, val="", secret=False, row=0):
        tk.Label(
            parent, text=label + ":",
            bg="#f0f4f8",
            font=("Segoe UI", 10, "bold")
        ).grid(row=row, column=0, sticky="w", pady=5)
        var = tk.StringVar(value=val)
        self.vars[cle] = var
        tk.Entry(
            parent, textvariable=var,
            width=38,
            show="*" if secret else "",
            font=("Segoe UI", 10)
        ).grid(row=row, column=1, padx=10, pady=5)
        return var

    def _bienvenue(self):
        self.lbl_titre.config(text="Bienvenue dans Brother Scan Center")
        infos = [
            "Detection automatique imprimante et NAS",
            "Configuration Gmail SMTP securisee",
            "Mots de passe chiffres AES-256",
            "Modifiable a tout moment depuis l application"
        ]
        tk.Label(
            self.content,
            text="L assistant va configurer le logiciel en 5 etapes.",
            font=("Segoe UI", 11),
            bg="#f0f4f8"
        ).pack(pady=10)
        for info in infos:
            tk.Label(
                self.content,
                text=f"  OK  {info}",
                font=("Segoe UI", 10),
                bg="#f0f4f8", anchor="w"
            ).pack(fill="x", pady=2)

    def _imprimante(self):
        self.lbl_titre.config(text="Configuration imprimante")
        f = tk.Frame(self.content, bg="#f0f4f8")
        f.pack(fill="x")
        ip_var = self._field(
            f, "IP imprimante", "printer_ip",
            self.cfg.get("scanner", "ip") or "192.168.1.", row=0
        )
        self._field(
            f, "Modele", "printer_model",
            self.cfg.get("scanner", "model") or "DCP-9020CDW", row=1
        )
        self.lbl_ping = tk.Label(
            self.content, text="",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8"
        )
        self.lbl_ping.pack(anchor="w", pady=5)
        btn_f = tk.Frame(self.content, bg="#f0f4f8")
        btn_f.pack(anchor="w")
        tk.Button(
            btn_f, text="Detecter automatiquement",
            command=lambda: self._detecter(
                ip_var, "Brother", self.lbl_ping
            ),
            bg="#17a2b8", fg="white",
            relief="flat", padx=8
        ).pack(side="left")
        tk.Button(
            btn_f, text="Tester connexion",
            command=lambda: self._ping(
                ip_var.get(), self.lbl_ping
            ),
            bg="#28a745", fg="white",
            relief="flat", padx=8
        ).pack(side="left", padx=8)

    def _smtp(self):
        self.lbl_titre.config(text="Configuration Gmail")
        f = tk.Frame(self.content, bg="#f0f4f8")
        f.pack(fill="x")
        self._field(
            f, "Adresse Gmail", "smtp_email",
            self.cfg.get("smtp", "email") or "", row=0
        )
        self._field(
            f, "App Password", "smtp_password",
            self.cfg.get("smtp", "app_password") or "",
            secret=True, row=1
        )
        tk.Label(
            self.content,
            text="App Password : myaccount.google.com\n"
                 "Securite > Mots de passe des applications",
            font=("Segoe UI", 9),
            bg="#f0f4f8", fg="#6c757d"
        ).pack(anchor="w", pady=5)
        self.lbl_smtp = tk.Label(
            self.content, text="",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8"
        )
        self.lbl_smtp.pack(anchor="w")
        tk.Button(
            self.content,
            text="Tester connexion SMTP",
            command=self._tester_smtp,
            bg="#17a2b8", fg="white",
            relief="flat", padx=8
        ).pack(anchor="w")

    def _tester_smtp(self):
        try:
            s = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
            s.starttls()
            s.login(
                self.vars.get("smtp_email", tk.StringVar()).get(),
                self.vars.get("smtp_password", tk.StringVar()).get()
            )
            s.quit()
            self.lbl_smtp.config(
                text="Connexion SMTP OK", fg="#28a745"
            )
        except Exception as e:
            self.lbl_smtp.config(
                text=f"Echec : {e}", fg="#dc3545"
            )

    def _nas(self):
        self.lbl_titre.config(text="Configuration NAS QNAP")
        f = tk.Frame(self.content, bg="#f0f4f8")
        f.pack(fill="x")
        ip_var = self._field(
            f, "IP du NAS", "nas_ip",
            self.cfg.get("nas", "ip") or "192.168.1.", row=0
        )
        self._field(
            f, "Dossier partage", "nas_partage",
            self.cfg.get("nas", "partage") or "Scans_Brother", row=1
        )
        self._field(
            f, "Utilisateur", "nas_user",
            self.cfg.get("nas", "user") or "scanner_brother", row=2
        )
        self._field(
            f, "Mot de passe", "nas_password",
            self.cfg.get("nas", "password") or "",
            secret=True, row=3
        )
        self.lbl_nas = tk.Label(
            self.content, text="",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8"
        )
        self.lbl_nas.pack(anchor="w", pady=5)
        btn_f = tk.Frame(self.content, bg="#f0f4f8")
        btn_f.pack(anchor="w")
        tk.Button(
            btn_f, text="Detecter NAS",
            command=lambda: self._detecter(
                ip_var, "QNAP", self.lbl_nas
            ),
            bg="#17a2b8", fg="white",
            relief="flat", padx=8
        ).pack(side="left")
        tk.Button(
            btn_f, text="Tester connexion",
            command=self._tester_nas,
            bg="#28a745", fg="white",
            relief="flat", padx=8
        ).pack(side="left", padx=8)

    def _tester_nas(self):
        ip = self.vars.get("nas_ip", tk.StringVar()).get()
        par = self.vars.get("nas_partage", tk.StringVar()).get()
        usr = self.vars.get("nas_user", tk.StringVar()).get()
        pwd = self.vars.get("nas_password", tk.StringVar()).get()
        ch = f"\\\\{ip}\\{par}"
        r = subprocess.run(
            f'net use "{ch}" /user:{usr} {pwd}',
            shell=True, capture_output=True
        )
        subprocess.run(
            f'net use "{ch}" /delete',
            shell=True, capture_output=True
        )
        if r.returncode == 0:
            self.lbl_nas.config(
                text="Connexion NAS OK", fg="#28a745"
            )
        else:
            self.lbl_nas.config(
                text="Echec connexion NAS", fg="#dc3545"
            )

    def _stockage(self):
        self.lbl_titre.config(text="Dossiers de stockage")
        ip = self.vars.get("nas_ip", tk.StringVar()).get()
        par = self.vars.get(
            "nas_partage", tk.StringVar(value="Scans_Brother")
        ).get()
        f = tk.Frame(self.content, bg="#f0f4f8")
        f.pack(fill="x")
        for row, (label, cle, defaut) in enumerate([
            ("Dossier scans", "scan_folder",
             f"\\\\{ip}\\{par}"),
            ("Dossier archives", "archive_folder",
             f"\\\\{ip}\\{par}\\Archives")
        ]):
            tk.Label(
                f, text=label + ":",
                bg="#f0f4f8",
                font=("Segoe UI", 10, "bold")
            ).grid(row=row, column=0, sticky="w", pady=5)
            var = tk.StringVar(
                value=self.cfg.get("storage", cle) or defaut
            )
            self.vars[cle] = var
            tk.Entry(
                f, textvariable=var,
                width=32,
                font=("Segoe UI", 10)
            ).grid(row=row, column=1, padx=5)
            tk.Button(
                f, text="...",
                command=lambda k=cle: self.vars[k].set(
                    filedialog.askdirectory() or self.vars[k].get()
                ),
                bg="#6c757d", fg="white", relief="flat"
            ).grid(row=row, column=2)

        self.var_keep = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.content,
            text="Conserver copie locale apres envoi",
            variable=self.var_keep,
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=10)

    def _fin(self):
        self.lbl_titre.config(text="Configuration terminee !")
        tk.Label(
            self.content,
            text="Brother Scan Center est pret !",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f4f8", fg="#003087"
        ).pack(pady=15)
        for label, cle in [
            ("Imprimante", "printer_ip"),
            ("Email", "smtp_email"),
            ("NAS", "nas_ip")
        ]:
            val = self.vars.get(cle, tk.StringVar()).get()
            row = tk.Frame(
                self.content,
                bg="#e8f0fe", padx=10, pady=5
            )
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text=label,
                font=("Segoe UI", 10, "bold"),
                bg="#e8f0fe", width=12, anchor="w"
            ).pack(side="left")
            tk.Label(
                row, text=val,
                font=("Segoe UI", 10),
                bg="#e8f0fe", fg="#555"
            ).pack(side="left")

        self.var_autostart = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.content,
            text="Demarrer automatiquement avec Windows",
            variable=self.var_autostart,
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=10)

    def _detecter(self, ip_var, type_app, lbl):
        lbl.config(text="Recherche en cours...", fg="#555")
        def scan():
            from core.network_discovery import NetworkDiscovery
            nd = NetworkDiscovery()
            res = nd.scanner_reseau()
            trouves = [
                r for r in res
                if type_app in r.get("type", "")
            ]
            if trouves:
                ip_var.set(trouves[0]["ip"])
                lbl.config(
                    text=f"Detecte : {trouves[0]['ip']}",
                    fg="#28a745"
                )
            else:
                lbl.config(
                    text="Non detecte, entrez l IP manuellement",
                    fg="#dc3545"
                )
        threading.Thread(target=scan, daemon=True).start()

    def _ping(self, ip, lbl):
        r = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True
        )
        if r.returncode == 0:
            lbl.config(text=f"{ip} repond", fg="#28a745")
        else:
            lbl.config(text=f"{ip} ne repond pas", fg="#dc3545")

    def _sauvegarder(self):
        mapping = {
            "printer_ip":     ("scanner", "ip"),
            "printer_model":  ("scanner", "model"),
            "smtp_email":     ("smtp", "email"),
            "smtp_password":  ("smtp", "app_password"),
            "nas_ip":         ("nas", "ip"),
            "nas_partage":    ("nas", "partage"),
            "nas_user":       ("nas", "user"),
            "nas_password":   ("nas", "password"),
            "scan_folder":    ("storage", "scan_folder"),
            "archive_folder": ("storage", "archive_folder"),
        }
        for var_key, cfg_path in mapping.items():
            if var_key in self.vars:
                self.cfg.set(
                    self.vars[var_key].get(),
                    *cfg_path
                )
        self.cfg.sauvegarder(self.cfg.config)
