import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import logging
import smtplib
import subprocess
import shutil
from datetime import datetime
from core.scanner import BrotherScanner
from core.email_sender import EmailSender
from core.file_watcher import FileWatcher


class BrotherScanCenter(tk.Tk):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.scanner = BrotherScanner(cfg)
        self.mailer = EmailSender(cfg)
        self._demarrer_watcher()
        self.title("Brother Scan Center")
        self.geometry("950x660")
        self.configure(bg="#f0f4f8")
        self.protocol("WM_DELETE_WINDOW", self.iconify)
        self._build()
        self.after(500, self.verifier_imprimante)

    def _demarrer_watcher(self):
        dossier = self.cfg.get("storage", "scan_folder")
        if dossier and os.path.exists(dossier):
            self.watcher = FileWatcher(
                dossier, self.mailer, self._archiver
            )
            self.watcher.demarrer()

    def _archiver(self, fichier):
        archive = self.cfg.get("storage", "archive_folder")
        if archive:
            os.makedirs(archive, exist_ok=True)
            shutil.move(
                fichier,
                os.path.join(archive, os.path.basename(fichier))
            )

    def _build(self):
        hdr = tk.Frame(self, bg="#003087", height=65)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="Brother Scan Center",
            font=("Segoe UI", 18, "bold"),
            bg="#003087", fg="white"
        ).pack(side="left", padx=20, pady=12)
        self.lbl_printer = tk.Label(
            hdr, text="",
            font=("Segoe UI", 9),
            bg="#003087", fg="#a0c4ff"
        )
        self.lbl_printer.pack(side="right", padx=20)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        tabs = [
            ("Scanner",        self._tab_scan),
            ("Historique",     self._tab_historique),
            ("Email SMTP",     self._tab_smtp),
            ("Imprimante",     self._tab_imprimante),
            ("NAS",            self._tab_nas),
            ("Stockage",       self._tab_stockage),
            ("Destinataires",  self._tab_destinataires),
        ]
        for nom, builder in tabs:
            frame = tk.Frame(nb, bg="#f0f4f8")
            nb.add(frame, text=nom)
            builder(frame)

        self.status_var = tk.StringVar(value="Pret")
        tk.Label(
            self,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg="#003087", fg="white",
            anchor="w", padx=10
        ).pack(fill="x", side="bottom")

    def _label_entry(self, parent, label, val, row,
                     secret=False, width=35):
        tk.Label(
            parent, text=label + ":",
            bg="#f0f4f8",
            font=("Segoe UI", 10),
            width=20, anchor="w"
        ).grid(row=row, column=0, pady=6, sticky="w")
        var = tk.StringVar(value=val)
        tk.Entry(
            parent, textvariable=var,
            width=width,
            font=("Segoe UI", 10),
            show="*" if secret else ""
        ).grid(row=row, column=1, pady=6, padx=10)
        return var

    def _section(self, parent, titre):
        f = tk.LabelFrame(
            parent, text=titre,
            font=("Segoe UI", 11, "bold"),
            bg="#f0f4f8", padx=15, pady=12
        )
        f.pack(fill="x", padx=25, pady=15)
        return f

    def _tab_scan(self, f):
        sf = tk.LabelFrame(
            f, text="Etat imprimante",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8", padx=10, pady=10
        )
        sf.pack(fill="x", padx=20, pady=10)
        self.lbl_statut = tk.Label(
            sf, text="Verification...",
            font=("Segoe UI", 11),
            bg="#f0f4f8"
        )
        self.lbl_statut.pack(side="left")
        tk.Button(
            sf, text="Actualiser",
            command=self.verifier_imprimante,
            bg="#003087", fg="white",
            relief="flat", padx=8
        ).pack(side="right")

        of = tk.LabelFrame(
            f, text="Options",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8", padx=10, pady=10
        )
        of.pack(fill="x", padx=20, pady=5)

        tk.Label(
            of, text="Format:",
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w")
        self.fmt_var = tk.StringVar(
            value=self.cfg.get("scanner", "format") or "PDF"
        )
        ttk.Combobox(
            of, textvariable=self.fmt_var,
            values=["PDF", "JPG", "PNG", "TIFF"],
            width=8, state="readonly"
        ).grid(row=0, column=1, padx=8)

        tk.Label(
            of, text="Resolution:",
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).grid(row=0, column=2, sticky="w")
        self.res_var = tk.StringVar(
            value=str(self.cfg.get("scanner", "resolution") or 300)
        )
        ttk.Combobox(
            of, textvariable=self.res_var,
            values=["100", "150", "200", "300", "600"],
            width=6, state="readonly"
        ).grid(row=0, column=3, padx=8)

        tk.Label(
            of, text="Envoyer a:",
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", pady=8)
        dests = self.cfg.get("email_destinations") or []
        vals = [
            d["email"] if isinstance(d, dict) else d
            for d in dests
        ]
        self.dest_var = tk.StringVar()
        cb = ttk.Combobox(
            of, textvariable=self.dest_var,
            values=vals, width=32
        )
        cb.grid(row=1, column=1, columnspan=3, sticky="w", padx=8)
        if vals:
            cb.current(0)

        bf = tk.Frame(f, bg="#f0f4f8")
        bf.pack(pady=15)
        tk.Button(
            bf, text="Scanner et envoyer email",
            command=self.lancer_scan_email,
            bg="#003087", fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=25, pady=12
        ).grid(row=0, column=0, padx=10)
        tk.Button(
            bf, text="Scanner et sauvegarder",
            command=self.lancer_scan_dossier,
            bg="#28a745", fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=25, pady=12
        ).grid(row=0, column=1, padx=10)

        self.prog = ttk.Progressbar(
            f, mode="indeterminate", length=400
        )
        self.prog.pack(pady=8)
        self.lbl_scan = tk.Label(
            f, text="",
            font=("Segoe UI", 10),
            bg="#f0f4f8", fg="#555"
        )
        self.lbl_scan.pack()

    def _tab_historique(self, f):
        tb = tk.Frame(f, bg="#f0f4f8")
        tb.pack(fill="x", padx=20, pady=8)
        tk.Button(
            tb, text="Effacer",
            command=self._effacer_hist,
            bg="#dc3545", fg="white",
            relief="flat", padx=8
        ).pack(side="right")
        tk.Button(
            tb, text="Exporter CSV",
            command=self._exporter_hist,
            bg="#6c757d", fg="white",
            relief="flat", padx=8
        ).pack(side="right", padx=5)

        cols = ("Date", "Fichier", "Destinataire", "Statut")
        self.tree = ttk.Treeview(
            f, columns=cols, show="headings", height=18
        )
        for col, w in zip(cols, [150, 260, 200, 100]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        sb = ttk.Scrollbar(
            f, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(
            side="left", fill="both",
            expand=True, padx=(20, 0)
        )
        sb.pack(side="right", fill="y", padx=(0, 20))
        self.tree.tag_configure("ok", foreground="#28a745")
        self.tree.tag_configure("err", foreground="#dc3545")

    def _tab_smtp(self, f):
        card = self._section(f, "Configuration Gmail SMTP")
        smtp = self.cfg.config.get("smtp", {})
        self.smtp_vars = {}
        champs = [
            ("Serveur SMTP",  "server",
             smtp.get("server", "smtp.gmail.com")),
            ("Port",          "port",
             str(smtp.get("port", 587))),
            ("Adresse email", "email",
             smtp.get("email", "")),
            ("App Password",  "app_password",
             smtp.get("app_password", "")),
        ]
        for i, (label, cle, val) in enumerate(champs):
            self.smtp_vars[cle] = self._label_entry(
                card, label, val, i,
                secret=(cle == "app_password")
            )
        self.lbl_smtp_test = tk.Label(
            f, text="",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8"
        )
        self.lbl_smtp_test.pack(padx=25, anchor="w")
        bf = tk.Frame(f, bg="#f0f4f8")
        bf.pack(padx=25, pady=8, anchor="w")
        tk.Button(
            bf, text="Tester connexion",
            command=self._tester_smtp,
            bg="#17a2b8", fg="white",
            relief="flat", padx=12, pady=6
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            bf, text="Sauvegarder",
            command=self._save_smtp,
            bg="#003087", fg="white",
            relief="flat", padx=12, pady=6
        ).grid(row=0, column=1, padx=5)

    def _tab_imprimante(self, f):
        card = self._section(f, "Configuration imprimante")
        sc = self.cfg.config.get("scanner", {})
        self.sc_vars = {}
        champs = [
            ("Adresse IP", "ip",    sc.get("ip", "")),
            ("Modele",     "model", sc.get("model", "DCP-9020CDW")),
        ]
        for i, (label, cle, val) in enumerate(champs):
            self.sc_vars[cle] = self._label_entry(
                card, label, val, i
            )
        tk.Label(
            card, text="Resolution DPI:",
            bg="#f0f4f8",
            font=("Segoe UI", 10),
            width=20, anchor="w"
        ).grid(row=2, column=0, pady=6, sticky="w")
        self.sc_vars["resolution"] = tk.StringVar(
            value=str(sc.get("resolution", 300))
        )
        ttk.Combobox(
            card,
            textvariable=self.sc_vars["resolution"],
            values=["100", "150", "200", "300", "600"],
            width=10, state="readonly"
        ).grid(row=2, column=1, pady=6, padx=10, sticky="w")

        self.lbl_ping = tk.Label(
            f, text="",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8"
        )
        self.lbl_ping.pack(padx=25, anchor="w")
        bf = tk.Frame(f, bg="#f0f4f8")
        bf.pack(padx=25, pady=8, anchor="w")
        tk.Button(
            bf, text="Tester connexion",
            command=self.verifier_imprimante,
            bg="#17a2b8", fg="white",
            relief="flat", padx=12, pady=6
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            bf, text="Sauvegarder",
            command=self._save_scanner,
            bg="#003087", fg="white",
            relief="flat", padx=12, pady=6
        ).grid(row=0, column=1, padx=5)

    def _tab_nas(self, f):
        card = self._section(f, "Configuration NAS QNAP")
        nas = self.cfg.config.get("nas", {})
        self.nas_vars = {}
        champs = [
            ("IP du NAS",       "ip",       nas.get("ip", "")),
            ("Dossier partage", "partage",  nas.get("partage", "Scans_Brother")),
            ("Utilisateur",     "user",     nas.get("user", "")),
            ("Mot de passe",    "password", nas.get("password", "")),
        ]
        for i, (label, cle, val) in enumerate(champs):
            self.nas_vars[cle] = self._label_entry(
                card, label, val, i,
                secret=(cle == "password")
            )
        self.lbl_nas_test = tk.Label(
            f, text="",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8"
        )
        self.lbl_nas_test.pack(padx=25, anchor="w")
        bf = tk.Frame(f, bg="#f0f4f8")
        bf.pack(padx=25, pady=8, anchor="w")
        tk.Button(
            bf, text="Tester connexion NAS",
            command=self._tester_nas,
            bg="#17a2b8", fg="white",
            relief="flat", padx=12, pady=6
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            bf, text="Sauvegarder",
            command=self._save_nas,
            bg="#003087", fg="white",
            relief="flat", padx=12, pady=6
        ).grid(row=0, column=1, padx=5)

    def _tab_stockage(self, f):
        card = self._section(f, "Dossiers de stockage")
        st = self.cfg.config.get("storage", {})
        self.st_vars = {}
        for i, (label, cle, defaut) in enumerate([
            ("Dossier scans",    "scan_folder",
             st.get("scan_folder", "")),
            ("Dossier archives", "archive_folder",
             st.get("archive_folder", ""))
        ]):
            tk.Label(
                card, text=label + ":",
                bg="#f0f4f8",
                font=("Segoe UI", 10),
                width=20, anchor="w"
            ).grid(row=i, column=0, pady=6, sticky="w")
            var = tk.StringVar(value=defaut)
            self.st_vars[cle] = var
            tk.Entry(
                card, textvariable=var,
                width=30,
                font=("Segoe UI", 10)
            ).grid(row=i, column=1, padx=5)
            tk.Button(
                card, text="...",
                command=lambda k=cle: self.st_vars[k].set(
                    filedialog.askdirectory() or self.st_vars[k].get()
                ),
                bg="#6c757d", fg="white", relief="flat"
            ).grid(row=i, column=2)

        self.keep_var = tk.BooleanVar(
            value=st.get("keep_local", True)
        )
        tk.Checkbutton(
            card,
            text="Conserver copie locale apres envoi",
            variable=self.keep_var,
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=8)

        tk.Button(
            f, text="Sauvegarder",
            command=self._save_stockage,
            bg="#003087", fg="white",
            relief="flat", padx=12, pady=6
        ).pack(padx=25, anchor="w", pady=5)

    def _tab_destinataires(self, f):
        card = self._section(f, "Gestion des destinataires")
        af = tk.Frame(card, bg="#f0f4f8")
        af.pack(fill="x", pady=5)

        tk.Label(
            af, text="Email:",
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).pack(side="left")
        self.new_email = tk.StringVar()
        tk.Entry(
            af, textvariable=self.new_email,
            width=28,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=8)

        tk.Label(
            af, text="Nom:",
            bg="#f0f4f8",
            font=("Segoe UI", 10)
        ).pack(side="left")
        self.new_nom = tk.StringVar()
        tk.Entry(
            af, textvariable=self.new_nom,
            width=18,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=8)

        tk.Button(
            af, text="Ajouter",
            command=self._ajouter_dest,
            bg="#28a745", fg="white",
            relief="flat", padx=8
        ).pack(side="left")

        self.dest_tree = ttk.Treeview(
            card,
            columns=("Email", "Nom"),
            show="headings", height=10
        )
        self.dest_tree.heading("Email", text="Adresse Email")
        self.dest_tree.heading("Nom", text="Nom")
        self.dest_tree.column("Email", width=280)
        self.dest_tree.column("Nom", width=180)
        self.dest_tree.pack(fill="both", expand=True, pady=8)
        self._charger_dests()

        bf = tk.Frame(card, bg="#f0f4f8")
        bf.pack(fill="x")
        tk.Button(
            bf, text="Supprimer selection",
            command=self._suppr_dest,
            bg="#dc3545", fg="white",
            relief="flat", padx=8
        ).pack(side="right")
        tk.Button(
            bf, text="Sauvegarder",
            command=self._save_dests,
            bg="#003087", fg="white",
            relief="flat", padx=8
        ).pack(side="right", padx=5)

    def lancer_scan_email(self):
        dest = self.dest_var.get()
        if not dest:
            messagebox.showwarning(
                "Attention", "Selectionnez un destinataire"
            )
            return
        threading.Thread(
            target=self._scan_thread,
            args=(dest, True),
            daemon=True
        ).start()

    def lancer_scan_dossier(self):
        threading.Thread(
            target=self._scan_thread,
            args=(None, False),
            daemon=True
        ).start()

    def _scan_thread(self, dest, envoyer):
        self.prog.start()
        self.lbl_scan.config(text="Scan en cours...")
        self.status_var.set("Scan en cours...")
        fichier = self.scanner.scanner_document()
        statut = "Echec"
        if fichier:
            if envoyer and dest:
                self.lbl_scan.config(text="Envoi email...")
                ok = self.mailer.envoyer(fichier, [dest])
                statut = "Envoye" if ok else "Erreur email"
            else:
                statut = "Sauvegarde"
            self._ajouter_hist(fichier, dest or "-", statut)
        self.prog.stop()
        self.lbl_scan.config(text=statut)
        self.status_var.set(statut)

    def verifier_imprimante(self):
        ip = self.cfg.get("scanner", "ip") or ""
        if not ip:
            self.lbl_statut.config(
                text="IP non configuree", fg="#dc3545"
            )
            return
        r = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True
        )
        if r.returncode == 0:
            self.lbl_statut.config(
                text=f"Imprimante connectee ({ip})",
                fg="#28a745"
            )
            self.lbl_printer.config(
                text=f"DCP-9020CDW - {ip}"
            )
        else:
            self.lbl_statut.config(
                text=f"Imprimante non joignable ({ip})",
                fg="#dc3545"
            )

    def _tester_smtp(self):
        try:
            s = smtplib.SMTP(
                self.smtp_vars["server"].get(),
                int(self.smtp_vars["port"].get()),
                timeout=10
            )
            s.starttls()
            s.login(
                self.smtp_vars["email"].get(),
                self.smtp_vars["app_password"].get()
            )
            s.quit()
            self.lbl_smtp_test.config(
                text="Connexion SMTP OK", fg="#28a745"
            )
        except Exception as e:
            self.lbl_smtp_test.config(
                text=f"Echec : {e}", fg="#dc3545"
            )

    def _tester_nas(self):
        ip = self.nas_vars["ip"].get()
        par = self.nas_vars["partage"].get()
        usr = self.nas_vars["user"].get()
        pwd = self.nas_vars["password"].get()
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
            self.lbl_nas_test.config(
                text="Connexion NAS OK", fg="#28a745"
            )
        else:
            self.lbl_nas_test.config(
                text="Echec connexion NAS", fg="#dc3545"
            )

    def _ajouter_dest(self):
        email = self.new_email.get().strip()
        nom = self.new_nom.get().strip()
        if email:
            self.dest_tree.insert(
                "", "end", values=(email, nom)
            )
            self.new_email.set("")
            self.new_nom.set("")

    def _suppr_dest(self):
        for item in self.dest_tree.selection():
            self.dest_tree.delete(item)

    def _charger_dests(self):
        for d in self.cfg.get("email_destinations") or []:
            if isinstance(d, dict):
                self.dest_tree.insert(
                    "", "end",
                    values=(d["email"], d.get("nom", ""))
                )
            else:
                self.dest_tree.insert("", "end", values=(d, ""))

    def _ajouter_hist(self, fichier, dest, statut):
        date = datetime.now().strftime("%d/%m/%Y %H:%M")
        nom = os.path.basename(fichier)
        tag = "ok" if statut in ("Envoye", "Sauvegarde") else "err"
        self.tree.insert(
            "", 0,
            values=(date, nom, dest, statut),
            tags=(tag,)
        )

    def _effacer_hist(self):
        if messagebox.askyesno("Confirmer", "Effacer l historique ?"):
            for i in self.tree.get_children():
                self.tree.delete(i)

    def _exporter_hist(self):
        f = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if f:
            with open(f, "w", encoding="utf-8") as fp:
                fp.write("Date,Fichier,Destinataire,Statut\n")
                for item in self.tree.get_children():
                    vals = self.tree.item(item)["values"]
                    fp.write(
                        ",".join(str(v) for v in vals) + "\n"
                    )
            messagebox.showinfo("Export", f"Exporte : {f}")

    def _save_smtp(self):
        for cle, var in self.smtp_vars.items():
            v = var.get()
            self.cfg.set(
                int(v) if cle == "port" else v,
                "smtp", cle
            )
        self.cfg.sauvegarder(self.cfg.config)
        messagebox.showinfo("OK", "Configuration SMTP sauvegardee")

    def _save_scanner(self):
        for cle, var in self.sc_vars.items():
            v = var.get()
            self.cfg.set(
                int(v) if cle == "resolution" else v,
                "scanner", cle
            )
        self.cfg.sauvegarder(self.cfg.config)
        messagebox.showinfo(
            "OK", "Configuration imprimante sauvegardee"
        )

    def _save_nas(self):
        for cle, var in self.nas_vars.items():
            self.cfg.set(var.get(), "nas", cle)
        self.cfg.sauvegarder(self.cfg.config)
        messagebox.showinfo("OK", "Configuration NAS sauvegardee")

    def _save_stockage(self):
        for cle, var in self.st_vars.items():
            self.cfg.set(var.get(), "storage", cle)
        self.cfg.set(
            self.keep_var.get(), "storage", "keep_local"
        )
        self.cfg.sauvegarder(self.cfg.config)
        messagebox.showinfo(
            "OK", "Configuration stockage sauvegardee"
        )

    def _save_dests(self):
        dests = []
        for item in self.dest_tree.get_children():
            email, nom = self.dest_tree.item(item)["values"]
            dests.append({"email": email, "nom": nom})
        self.cfg.set(dests, "email_destinations")
        self.cfg.sauvegarder(self.cfg.config)
        messagebox.showinfo("OK", "Destinataires sauvegardes")
