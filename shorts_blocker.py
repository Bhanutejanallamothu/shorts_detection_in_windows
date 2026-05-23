"""
YouTube Shorts Blocker - Windows Prototype
Two-stage detection:
  Stage 1: Read window title silently (no keypresses) — check if YouTube is open
  Stage 2: Only THEN grab the URL — confirms it's exactly youtube.com/shorts/
This prevents constant address bar interruptions while browsing other sites.
"""

import time
import threading
import subprocess
import sys
import re
import ctypes

# ── Auto-install dependencies ──
def _ensure(pkg, import_name=None):
    name = import_name or pkg
    try:
        __import__(name)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

_ensure("psutil")
_ensure("pyautogui")
_ensure("pyperclip")

import psutil
import pyautogui
import pyperclip

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
CHECK_INTERVAL      = 2.0    # How often to run the title check (seconds)
URL_GRAB_INTERVAL   = 2.0    # Min seconds between URL grabs (when on YouTube)

BROWSER_PROCESS_NAMES = [
    "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe",
]

SHORTS_URL_PATTERN = re.compile(
    r"https?://(www\.)?youtube\.com/shorts/",
    re.IGNORECASE
)

# ─────────────────────────────────────────────
# STAGE 1 — Silent title check (no keypresses)
# ─────────────────────────────────────────────

def get_active_window_title() -> str:
    """Read the window title bar — completely silent, no keypresses."""
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


def is_youtube_in_title() -> bool:
    """
    Stage 1 gate: silently check if YouTube is likely open.
    Browser titles look like:  'My Video - YouTube - Google Chrome'
    This check costs zero keypresses — just reads the title bar.
    """
    title = get_active_window_title().lower()
    return "youtube" in title


# ─────────────────────────────────────────────
# STAGE 2 — URL grab (only runs when on YouTube)
# ─────────────────────────────────────────────

def get_current_url() -> str:
    """
    Grab the real URL from the address bar.
    Only called after Stage 1 confirms YouTube is open,
    so this interruption is rare and expected.
    """
    try:
        old_clipboard = ""
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            pass

        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.15)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.1)
        pyautogui.press("escape")        # Immediately unfocus — barely noticeable
        time.sleep(0.05)

        url = pyperclip.paste().strip()

        try:
            if old_clipboard:
                pyperclip.copy(old_clipboard)
        except Exception:
            pass

        return url

    except Exception as e:
        print(f"  [URL READ ERROR] {e}")
        return ""


def is_youtube_shorts_url(url: str) -> bool:
    return bool(SHORTS_URL_PATTERN.match(url))


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
        self._last_blocked_url = ""
        self._last_url_grab    = 0.0     # timestamp of last Ctrl+L grab

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        while self.running:
            try:
                if not is_browser_active():
                    # Not even a browser — skip everything silently
                    time.sleep(CHECK_INTERVAL)
                    continue

                # ── Stage 1: silent title check ──
                if not is_youtube_in_title():
                    # Browser is open but not on YouTube — do nothing
                    print("  [STAGE1] Browser active, not YouTube — skipping URL grab")
                    self._last_blocked_url = ""
                    time.sleep(CHECK_INTERVAL)
                    continue

                # ── Stage 2: YouTube is open — now grab the URL ──
                now = time.time()
                if now - self._last_url_grab < URL_GRAB_INTERVAL:
                    # Too soon since last grab — wait
                    time.sleep(CHECK_INTERVAL)
                    continue

                self._last_url_grab = now
                url = get_current_url()
                print(f"  [STAGE2] URL grabbed: {url[:80]}")

                if url and is_youtube_shorts_url(url):
                    if url != self._last_blocked_url:
                        self._last_blocked_url = url
                        print(f"  [BLOCKED] Shorts confirmed: {url}")
                        time.sleep(0.3)
                        closed = close_tab()
                        if closed:
                            self.blocked_count += 1
                            if self.on_status_update:
                                self.on_status_update(
                                    f"Blocked! ({self.blocked_count} total)"
                                )
                else:
                    self._last_blocked_url = ""

            except Exception as e:
                print(f"  [ERROR] {e}")

            time.sleep(CHECK_INTERVAL)