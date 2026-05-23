"""
YouTube Shorts Blocker — GUI
Run this file to launch the app.
"""

import tkinter as tk
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from shorts_blocker import ShortsBlocker

BG         = "#0f0f0f"
CARD       = "#1a1a1a"
BORDER     = "#2a2a2a"
RED        = "#ff0033"
RED_DARK   = "#cc0026"
GREEN      = "#00e676"
TEXT       = "#ffffff"
TEXT_DIM   = "#888888"
TEXT_MUTED = "#444444"
YELLOW     = "#ffd600"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shorts Blocker")
        self.geometry("400x560")
        self.resizable(False, False)
        self.configure(bg=BG)
        x = (self.winfo_screenwidth()  // 2) - 200
        y = (self.winfo_screenheight() // 2) - 280
        self.geometry(f"+{x}+{y}")

        self.blocker = ShortsBlocker(on_status_update=self._on_blocked)
        self.is_on   = False
        self._build_ui()

    def _build_ui(self):
        # Title
        top = tk.Frame(self, bg=BG, pady=20)
        top.pack(fill="x")
        tk.Label(top, text="▶  SHORTS BLOCKER", bg=BG, fg=RED,
                 font=("Courier New", 13, "bold")).pack()
        tk.Label(top, text="YouTube Shorts auto-closer for Windows",
                 bg=BG, fg=TEXT_DIM, font=("Courier New", 8)).pack(pady=(2,0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # Status card
        card = tk.Frame(self, bg=CARD, pady=20, padx=24)
        card.pack(fill="x", padx=20, pady=20)

        row = tk.Frame(card, bg=CARD)
        row.pack(anchor="w")
        self.dot = tk.Label(row, text="●", bg=CARD, fg=TEXT_MUTED,
                            font=("Courier New", 18))
        self.dot.pack(side="left")
        self.status_label = tk.Label(row, text="  INACTIVE", bg=CARD,
                                     fg=TEXT_MUTED, font=("Courier New", 14, "bold"))
        self.status_label.pack(side="left")

        self.sub_label = tk.Label(card, text="Turn on the blocker to get started",
                                  bg=CARD, fg=TEXT_DIM, font=("Courier New", 8))
        self.sub_label.pack(anchor="w", pady=(6,0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # Toggle button
        btn_frame = tk.Frame(self, bg=BG, pady=20)
        btn_frame.pack()
        self.toggle_btn = tk.Button(btn_frame, text="TURN  ON",
            bg=RED, fg=TEXT, activebackground=RED_DARK, activeforeground=TEXT,
            font=("Courier New", 14, "bold"), width=16, height=2,
            bd=0, cursor="hand2", command=self._toggle)
        self.toggle_btn.pack()

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # Detection method badge
        method_frame = tk.Frame(self, bg=BG, pady=10, padx=20)
        method_frame.pack(fill="x")
        tk.Label(method_frame, text="DETECTION METHOD",
                 bg=BG, fg=TEXT_DIM, font=("Courier New", 8, "bold")).pack(anchor="w")
        self.method_label = tk.Label(method_frame,
            text="⬤  Title bar (fallback)",
            bg=BG, fg=YELLOW, font=("Courier New", 9))
        self.method_label.pack(anchor="w", pady=(3,0))
        tk.Label(method_frame,
            text="Tip: launch Chrome with --remote-debugging-port=9222\nfor zero-keypress exact URL detection",
            bg=BG, fg=TEXT_MUTED, font=("Courier New", 7), justify="left").pack(anchor="w", pady=(3,0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # Stats
        stats = tk.Frame(self, bg=BG, pady=14, padx=20)
        stats.pack(fill="x")
        tk.Label(stats, text="TABS CLOSED", bg=BG, fg=TEXT_DIM,
                 font=("Courier New", 8)).pack(side="left")
        self.count_label = tk.Label(stats, text="0", bg=BG, fg=TEXT,
                                    font=("Courier New", 22, "bold"))
        self.count_label.pack(side="right")

    def _toggle(self):
        if not self.is_on:
            self.is_on = True
            self.blocker.start()
            self.dot.config(fg=GREEN)
            self.status_label.config(text="  ACTIVE", fg=GREEN)
            self.sub_label.config(text="Watching for Shorts silently...")
            self.toggle_btn.config(text="TURN  OFF", bg="#222222",
                                   activebackground="#333333")
            self.after(1500, self._update_method_badge)
        else:
            self.is_on = False
            self.blocker.stop()
            self.dot.config(fg=TEXT_MUTED)
            self.status_label.config(text="  INACTIVE", fg=TEXT_MUTED)
            self.sub_label.config(text="Turn on the blocker to get started")
            self.toggle_btn.config(text="TURN  ON", bg=RED,
                                   activebackground=RED_DARK)

    def _update_method_badge(self):
        """Show which detection method is active after blocker has started."""
        if self.blocker._debug_available:
            self.method_label.config(
                text="⬤  Debug port (exact URL — zero keypresses)", fg=GREEN)
        elif self.blocker._debug_available is False:
            self.method_label.config(
                text="⬤  Title bar match (fallback — no keypresses)", fg=YELLOW)

    def _on_blocked(self, message: str):
        self.after(0, self._update_count)

    def _update_count(self):
        self.count_label.config(text=str(self.blocker.blocked_count))
        self.dot.config(fg="white")
        self.after(300, lambda: self.dot.config(fg=GREEN))

if __name__ == "__main__":
    app = App()
    app.mainloop()