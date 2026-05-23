"""
YouTube Shorts Blocker - Windows Prototype
Detects Shorts via window title — zero keypresses, zero interruptions.
"""

import time
import threading
import subprocess
import sys
import re
import ctypes

def _ensure(pkg, import_name=None):
    try:
        __import__(import_name or pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

_ensure("psutil")
_ensure("pyautogui")
_ensure("requests")

import psutil
import pyautogui
import requests

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
CHECK_INTERVAL = 2.0

BROWSER_PROCESS_NAMES = [
    "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe",
]

SHORTS_URL_PATTERN = re.compile(
    r"https?://(www\.)?youtube\.com/shorts/",
    re.IGNORECASE
)

# ─────────────────────────────────────────────
# WINDOW TITLE — zero keypresses
# ─────────────────────────────────────────────

def get_active_window_title() -> str:
    try:
        hwnd   = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf    = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def get_active_process_name() -> str:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        pid  = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return psutil.Process(pid.value).name().lower()
    except Exception:
        return ""


def is_browser_active() -> bool:
    return get_active_process_name() in BROWSER_PROCESS_NAMES


def is_shorts_via_title(title: str) -> bool:
    """
    Detect Shorts purely from the window title bar.

    Real Shorts titles seen in the wild:
      'Aura of Ishowspeed #shorts #ishowspeed - YouTube - Brave'
      '#illustration #tattoo #art #pov - YouTube - Brave'
      'YouTube Shorts - Brave'
      'Zombies ARC #countryballs #edit - YouTube - Brave'  ← NOT shorts (no #shorts tag)

    Rules:
      1. Title must end with '- YouTube - <browser>' so we only match YouTube tabs
      2. AND one of:
           a. Contains '#shorts' anywhere in title
           b. Title literally says 'YouTube Shorts' (Shorts homepage)
    """
    t = title.lower()

    # Rule 1: must be a YouTube browser tab
    is_youtube_tab = "- youtube -" in t or t.startswith("youtube shorts -")
    if not is_youtube_tab:
        return False

    # Rule 2a: has the #shorts hashtag
    if "#shorts" in t:
        return True

    # Rule 2b: is the Shorts homepage/feed
    if "youtube shorts" in t:
        return True

    return False


# ─────────────────────────────────────────────
# DEBUG PORT (optional, more accurate)
# ─────────────────────────────────────────────

def get_url_via_debug_port() -> str:
    try:
        resp = requests.get("http://127.0.0.1:9222/json", timeout=1.0)
        for tab in resp.json():
            if tab.get("type") == "page":
                return tab.get("url", "")
        return ""
    except Exception:
        return ""


def is_youtube_shorts_url(url: str) -> bool:
    return bool(SHORTS_URL_PATTERN.match(url))


# ─────────────────────────────────────────────
# CLOSE TAB
# ─────────────────────────────────────────────

def close_tab():
    try:
        pyautogui.hotkey("ctrl", "w")
        return True
    except Exception as e:
        print(f"  [!] Could not close tab: {e}")
        return False


# ─────────────────────────────────────────────
# BLOCKER ENGINE
# ─────────────────────────────────────────────

class ShortsBlocker:
    def __init__(self, on_status_update=None):
        self.running           = False
        self.blocked_count     = 0
        self.on_status_update  = on_status_update
        self._thread           = None
        self._last_blocked_key = ""
        self._debug_available  = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _check_debug_port(self) -> bool:
        try:
            requests.get("http://127.0.0.1:9222/json", timeout=1.0)
            print("  [INFO] Debug port available — using exact URL detection")
            return True
        except Exception:
            print("  [INFO] Debug port not available — using title bar detection")
            return False

    def _is_shorts(self) -> tuple:
        """Returns (is_shorts: bool, key: str)"""

        if self._debug_available is None:
            self._debug_available = self._check_debug_port()

        if self._debug_available:
            url = get_url_via_debug_port()
            if url:
                result = is_youtube_shorts_url(url)
                print(f"  [CDP] {url[:70]} → {'SHORTS' if result else 'ok'}")
                return result, url
            self._debug_available = None

        # Title bar fallback
        title = get_active_window_title()
        result = is_shorts_via_title(title)
        print(f"  [TITLE] {title[:70]} → {'SHORTS ✓' if result else 'ok'}")
        return result, title

    def _monitor_loop(self):
        while self.running:
            try:
                if is_browser_active():
                    detected, key = self._is_shorts()

                    if detected:
                        if key != self._last_blocked_key:
                            self._last_blocked_key = key
                            print(f"  [BLOCKED] Closing Shorts tab")
                            time.sleep(0.3)
                            closed = close_tab()
                            if closed:
                                self.blocked_count += 1
                                if self.on_status_update:
                                    self.on_status_update(
                                        f"Blocked! ({self.blocked_count} total)"
                                    )
                    else:
                        self._last_blocked_key = ""

            except Exception as e:
                print(f"  [ERROR] {e}")

            time.sleep(CHECK_INTERVAL)