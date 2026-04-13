import tkinter as tk
from tkinter import ttk
import threading

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brother Scan Center")
        self.geometry("520x300")
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
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"520x300+{x}+{y}")

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
            text="Chargement...",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8",
            fg="#003087"
        )
        self.status.pack(anchor="w")

        self.bar = ttk.Progressbar(
            self.card,
            mode="indeterminate",
            length=460
        )
        self.bar.pack(fill="x", pady=10)
        self.bar.start(10)

        tk.Label(
            self,
            text="v1.0.0",
            font=("Segoe UI", 8),
            bg="#003087",
            fg="#6c9fd4"
        ).pack(side="bottom", pady=5)

    def _lancer(self):
        threading.Thread(target=self._charger, daemon=True).start()

    def _charger(self):
        import time
        self.status.config(text="Initialisation...")
        time.sleep(1)
        self.status.config(text="Chargement des modules...")
        time.sleep(1)
        self.status.config(text="Pret !")
        self.succes = True
        self.after(800, self.destroy)
