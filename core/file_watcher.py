import time, os, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ScanHandler(FileSystemEventHandler):
    def __init__(self, mailer, archiver):
        self.mailer  = mailer
        self.archiver = archiver

    def on_created(self, event):
        if event.is_directory:
            return
        f = event.src_path
        if not f.lower().endswith((".pdf",".jpg",".png",".tif")):
            return
        logging.info(f"Nouveau scan : {f}")
        time.sleep(3)
        if os.path.exists(f) and os.path.getsize(f) > 0:
            succes = self.mailer.envoyer(f)
            if succes and self.archiver:
                self.archiver(f)

class FileWatcher:
    def __init__(self, dossier, mailer, archiver=None):
        self.dossier  = dossier
        self.observer = Observer()
        handler       = ScanHandler(mailer, archiver)
        self.observer.schedule(handler, dossier, recursive=False)

    def demarrer(self):
        self.observer.start()
        logging.info(f"Watcher demarre sur {self.dossier}")

    def arreter(self):
        self.observer.stop()
        self.observer.join()
