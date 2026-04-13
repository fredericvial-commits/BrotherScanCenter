import pystray, threading, logging
from PIL import Image, ImageDraw

class TrayApp:
    def __init__(self, app):
        self.app  = app
        self.icon = None

    def _creer_image(self):
        img  = Image.new("RGB",(64,64),(0,48,135))
        draw = ImageDraw.Draw(img)
        draw.rectangle([12,18,52,42], fill="white")
        draw.rectangle([20,38,44,52], fill="white")
        draw.ellipse([44,20,54,30], fill=(0,200,80))
        return img

    def demarrer(self):
        menu = pystray.Menu(
            pystray.MenuItem("Scanner maintenant",
                lambda i,it: threading.Thread(
                    target=self.app.lancer_scan_email,
                    daemon=True).start()),
            pystray.MenuItem("Ouvrir",
                lambda i,it: self.app.deiconify()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter",
                lambda i,it: self._quitter())
        )
        self.icon = pystray.Icon(
            "BrotherScanCenter",
            self._creer_image(),
            "Brother Scan Center", menu)
        threading.Thread(
            target=self.icon.run, daemon=True).start()

    def _quitter(self):
        if self.icon:
            self.icon.stop()
        self.app.quit()
