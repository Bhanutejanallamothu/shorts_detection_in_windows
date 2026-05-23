"""
YouTube Shorts Blocker — GUI
Run this file to launch the app with a visual interface.
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import sys
import os

# Import our blocker logic
sys.path.insert(0, os.path.dirname(__file__))
from shorts_blocker import ShortsBlocker

# ─────────────────────────────────────────────
# COLORS & THEME
# ─────────────────────────────────────────────
BG          = "#0f0f0f"
CARD        = "#1a1a1a"
BORDER      = "#2a2a2a"
RED         = "#ff0033"       # YouTube red
RED_DARK    = "#cc0026"
GREEN       = "#00e676"
GREEN_DARK  = "#00c853"
TEXT        = "#ffffff"
TEXT_DIM    = "#888888"
TEXT_MUTED  = "#444444"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # ── Window setup ──
        self.title("Shorts Blocker")
        self.geometry("400x520")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 200
        y = (self.winfo_screenheight() // 2) - 260
        self.geometry(f"+{x}+{y}")

        # ── Blocker engine ──
        self.blocker = ShortsBlocker(on_status_update=self._on_blocked)
        self.is_on = False

        self._build_ui()

    # ─────────────────────────────────────────
    # BUILD UI
    # ─────────────────────────────────────────
    def _build_ui(self):

        # ── Top bar ──
        top = tk.Frame(self, bg=BG, pady=20)
        top.pack(fill="x")

        tk.Label(
            top, text="▶  SHORTS BLOCKER",
            bg=BG, fg=RED,
            font=("Courier New", 13, "bold"),
        ).pack()

        tk.Label(
            top, text="YouTube Shorts auto-closer for Windows",
            bg=BG, fg=TEXT_DIM,
            font=("Courier New", 8),
        ).pack(pady=(2, 0))

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── Status card ──
        card = tk.Frame(self, bg=CARD, bd=0, pady=24, padx=24)
        card.pack(fill="x", padx=20, pady=20)

        # Status dot + label row
        status_row = tk.Frame(card, bg=CARD)
        status_row.pack(anchor="w")

        self.dot = tk.Label(
            status_row, text="●",
            bg=CARD, fg=TEXT_MUTED,
            font=("Courier New", 18),
        )
        self.dot.pack(side="left")

        self.status_label = tk.Label(
            status_row, text="  INACTIVE",
            bg=CARD, fg=TEXT_MUTED,
            font=("Courier New", 14, "bold"),
        )
        self.status_label.pack(side="left")

        # Subtitle status
        self.sub_label = tk.Label(
            card,
            text="Turn on the blocker to get started",
            bg=CARD, fg=TEXT_DIM,
            font=("Courier New", 8),
        )
        self.sub_label.pack(anchor="w", pady=(6, 0))

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── Big toggle button ──
        btn_frame = tk.Frame(self, bg=BG, pady=24)
        btn_frame.pack()

        self.toggle_btn = tk.Button(
            btn_frame,
            text="TURN  ON",
            bg=RED, fg=TEXT,
            activebackground=RED_DARK,
            activeforeground=TEXT,
            font=("Courier New", 14, "bold"),
            width=16, height=2,
            bd=0, cursor="hand2",
            command=self._toggle,
        )
        self.toggle_btn.pack()

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── Stats row ──
        stats = tk.Frame(self, bg=BG, pady=16)
        stats.pack(fill="x", padx=20)

        tk.Label(
            stats, text="TABS CLOSED",
            bg=BG, fg=TEXT_DIM,
            font=("Courier New", 8),
        ).pack(side="left")

        self.count_label = tk.Label(
            stats, text="0",
            bg=BG, fg=TEXT,
            font=("Courier New", 22, "bold"),
        )
        self.count_label.pack(side="right")

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── How it works ──
        info = tk.Frame(self, bg=BG, pady=16, padx=20)
        info.pack(fill="x")

        tk.Label(
            info, text="HOW IT WORKS",
            bg=BG, fg=TEXT_DIM,
            font=("Courier New", 8, "bold"),
        ).pack(anchor="w")

        steps = [
            "1. Turn ON the blocker above",
            "2. Open YouTube in your browser",
            "3. Navigate to a Shorts video",
            "4. Tab closes automatically ✓",
        ]
        for step in steps:
            tk.Label(
                info, text=step,
                bg=BG, fg=TEXT_MUTED,
                font=("Courier New", 8),
                justify="left",
            ).pack(anchor="w", pady=1)

    # ─────────────────────────────────────────
    # TOGGLE ON/OFF
    # ─────────────────────────────────────────
    def _toggle(self):
        if not self.is_on:
            self._turn_on()
        else:
            self._turn_off()

    def _turn_on(self):
        self.is_on = True
        self.blocker.start()

        self.dot.config(fg=GREEN)
        self.status_label.config(text="  ACTIVE", fg=GREEN)
        self.sub_label.config(text="Watching your browser for Shorts...")
        self.toggle_btn.config(text="TURN  OFF", bg="#222222", activebackground="#333333")

    def _turn_off(self):
        self.is_on = False
        self.blocker.stop()

        self.dot.config(fg=TEXT_MUTED)
        self.status_label.config(text="  INACTIVE", fg=TEXT_MUTED)
        self.sub_label.config(text="Turn on the blocker to get started")
        self.toggle_btn.config(text="TURN  ON", bg=RED, activebackground=RED_DARK)

    # ─────────────────────────────────────────
    # CALLBACK WHEN SHORTS BLOCKED
    # ─────────────────────────────────────────
    def _on_blocked(self, message: str):
        # Update count label (must run on main thread)
        self.after(0, self._update_count)

    def _update_count(self):
        self.count_label.config(text=str(self.blocker.blocked_count))
        # Flash the dot briefly white
        self.dot.config(fg="white")
        self.after(300, lambda: self.dot.config(fg=GREEN))


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()