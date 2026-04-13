import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def creer_raccourci():
    """Crée un raccourci sur le Bureau au premier lancement."""
    try:
        import win32com.client
        bureau = os.path.join(os.path.expanduser("~"), "Desktop")
        raccourci = os.path.join(bureau, "Brother Scan Center.lnk")
        if not os.path.exists(raccourci):
            shell = win32com.client.Dispatch("WScript.Shell")
            lnk = shell.CreateShortcut(raccourci)
            if getattr(sys, 'frozen', False):
                lnk.TargetPath = sys.executable
                lnk.WorkingDirectory = os.path.dirname(
                    sys.executable
                )
            else:
                lnk.TargetPath = sys.executable
                lnk.Arguments = os.path.abspath(__file__)
                lnk.WorkingDirectory = os.path.dirname(
                    os.path.abspath(__file__)
                )
            lnk.Description = "Brother Scan Center - DCP-9020CDW"
            lnk.save()
    except Exception:
        pass


def connecter_nas(cfg):
    """Connecte automatiquement le NAS au démarrage."""
    try:
        ip = cfg.get("nas", "ip") or ""
        partage = cfg.get("nas", "partage") or "Scans_Brother"
        user = cfg.get("nas", "user") or ""
        password = cfg.get("nas", "password") or ""

        if not ip or not user:
            return

        chemin = f"\\\\{ip}\\{partage}"

        # Déconnecter d'abord si déjà connecté
        subprocess.run(
            f'net use "{chemin}" /delete /y',
            shell=True,
            capture_output=True
        )

        # Reconnecter avec les bons identifiants
        r = subprocess.run(
            f'net use "{chemin}" /user:{user} {password} /persistent:yes',
            shell=True,
            capture_output=True,
            text=True
        )

        if r.returncode == 0:
            print(f"NAS connecte : {chemin}")
        else:
            print(f"Erreur connexion NAS : {r.stderr}")

        # Connecter aussi le dossier archives
        archive = cfg.get("storage", "archive_folder") or ""
        if archive and not os.path.exists(archive):
            os.makedirs(archive, exist_ok=True)

    except Exception as e:
        print(f"Exception connexion NAS : {e}")


def main():
    if sys.version_info < (3, 8):
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "Python 3.8 minimum requis.\npython.org",
            "Erreur",
            0x10
        )
        sys.exit(1)

    creer_raccourci()

    from bootstrap import SplashScreen
    splash = SplashScreen()
    splash.mainloop()
    if not splash.succes:
        sys.exit(1)

    from config_manager import ConfigManager
    cfg = ConfigManager()

    if cfg.get("app", "first_run") is not False:
        from ui.setup_wizard_ui import SetupWizard
        wizard = SetupWizard(cfg)
        wizard.mainloop()
        if not wizard.configure_ok:
            sys.exit(0)
        cfg.set(False, "app", "first_run")
        cfg.sauvegarder(cfg.config)

    # Connexion automatique au NAS
    connecter_nas(cfg)

    from ui.main_window import BrotherScanCenter
    from ui.tray import TrayApp
    app = BrotherScanCenter(cfg)
    tray = TrayApp(app)
    tray.demarrer()
    app.mainloop()


if __name__ == "__main__":
    main()
