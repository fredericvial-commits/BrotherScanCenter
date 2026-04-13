import smtplib, os, logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

class EmailSender:
    def __init__(self, cfg):
        self.cfg = cfg

    def envoyer(self, fichier_path, destinataires=None):
        if destinataires is None:
            dests = self.cfg.get("email_destinations") or []
            destinataires = [
                d["email"] if isinstance(d,dict) else d
                for d in dests]
        if not destinataires:
            logging.warning("Aucun destinataire")
            return False
        nom  = os.path.basename(fichier_path)
        date = datetime.now().strftime("m/H:M")
        msg  = MIMEMultipart()
        msg["From"]    = self.cfg.get("smtp","email") or ""
        msg["To"]      = ", ".join(destinataires)
        msg["Subject"] = f"Scan Brother — {date}"
        msg.attach(MIMEText(
            f"Document scanne le {date}\nFichier : {nom}",
            "plain","utf-8"))
        with open(fichier_path,"rb") as f:
            part = MIMEBase("application","octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",
            f"attachment; filename={nom}")
        msg.attach(part)
        try:
            with smtplib.SMTP(
                    self.cfg.get("smtp","server") or "smtp.gmail.com",
                    int(self.cfg.get("smtp","port") or 587)) as s:
                s.starttls()
                s.login(self.cfg.get("smtp","email"),
                         self.cfg.get("smtp","app_password"))
                s.sendmail(msg["From"], destinataires, msg.as_string())
            logging.info(f"Email envoye a {destinataires}")
            return True
        except Exception as e:
            logging.error(f"Erreur email : {e}")
            return False
