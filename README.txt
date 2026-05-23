# YouTube Shorts Blocker — Windows Prototype

Automatically closes browser tabs when YouTube Shorts is detected.
Works silently in the background — **zero keypresses, zero interruptions.**

---

## Files in This Project

```
shorts_blocker_gui.py   ← Run this to launch the app
shorts_blocker.py       ← The brain — detection and blocking logic
debug_test.py           ← Diagnostic tool (run this if something breaks)
README.md               ← This file
```

Both `.py` files must stay in the **same folder** at all times.  
Only ever run `shorts_blocker_gui.py` — it loads the other file automatically.

---

## Setup (One Time Only)

### Step 1 — Install Python
Download from **https://python.org/downloads**  
During install: tick the box **"Add Python to PATH"** before clicking Install.

### Step 2 — Install required libraries
Open Command Prompt and run:
```
pip install psutil pyautogui requests
```

### Step 3 — Run the app
Double-click `shorts_blocker_gui.py`  
OR open Command Prompt in the folder and run:
```
python shorts_blocker_gui.py
```

### Step 4 — Turn it on
Click **TURN ON** in the app window. Done.

---

## How Each File Works

### `shorts_blocker_gui.py` — The Visual App

This is the window you see on screen. It does three things:

- Shows whether the blocker is **ON or OFF**
- Shows a **tab counter** — how many Shorts tabs have been closed
- Shows which **detection method** is active (see below)
- Has a **TURN ON / TURN OFF** button

When you click TURN ON, it starts the blocker engine from `shorts_blocker.py`
running in the background. When you click TURN OFF, it stops it.
The GUI itself does no detection — it only controls and displays.

---

### `shorts_blocker.py` — The Detection Engine

This is the brain. It runs a loop every 2 seconds and does the following:

```
Every 2 seconds:
    Is a browser the active window?
        NO  → do nothing, sleep
        YES → check if Shorts is open (see detection below)
                  Shorts detected? → close the tab
                  Not Shorts?      → do nothing, sleep
```

It runs on a background thread so it never freezes the GUI.

---

## How Shorts Is Detected

There are two detection methods. The app automatically picks the best one available.

---

### Method A — Debug Port (Best)
**Accuracy: exact URL match | Keypresses: zero**

Chrome, Edge, and Brave have a built-in developer tool called **Chrome DevTools Protocol (CDP)**.
When enabled, the app can ask the browser directly:
> "What URL is open in the current tab?"

The browser answers instantly over a local connection — no touching the keyboard or clipboard at all.

The app then checks if the URL matches this pattern:
```
https://www.youtube.com/shorts/
```

**To enable this method:**
1. Right-click your Chrome or Brave shortcut → **Properties**
2. In the **Target** field, add this to the very end:
   ```
   --remote-debugging-port=9222
   ```
   Example of what the full target looks like:
   ```
   "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
   ```
3. Click OK and relaunch the browser from that shortcut

Once enabled, the GUI shows a **green badge** confirming this method is active.

---

### Method B — Window Title Bar (Fallback)
**Accuracy: hashtag match | Keypresses: zero**

If the debug port is not set up, the app reads the browser's **window title bar**.
Windows gives this information for free — no keypress needed at all.

Every browser tab shows its page title in the window title bar. For YouTube, it looks like:

```
Video Title - YouTube - Brave
```

The app uses two rules to decide if it is Shorts:

**Rule 1 — Is this even a YouTube tab?**
The title must contain `- YouTube -` (with the browser name after).
This filters out every other tab — Gmail, Google, this README, everything else.

```
Android TV - Claude - Brave          ← NO  (not YouTube)
New Tab - Brave                      ← NO  (not YouTube)
Zombies ARC - YouTube - Brave        ← YES (is YouTube) → proceed to Rule 2
```

**Rule 2 — Is this specifically Shorts?**
Two checks, either one triggers a block:

| Check | What it looks for | Example |
|---|---|---|
| `#shorts` tag | The video title contains the hashtag `#shorts` | `Aura of Ishowspeed #shorts - YouTube - Brave` |
| Shorts homepage | Title starts with `YouTube Shorts` | `YouTube Shorts - Brave` |

If neither matches, the tab is left alone — even if it's a YouTube video.

---

## How It Tells Shorts Apart From Other Tabs

Here is a full comparison of how every tab type is handled:

| Tab | Title bar text | Blocked? | Why |
|---|---|---|---|
| YouTube Shorts video | `Dance #shorts - YouTube - Brave` | ✅ Yes | Has `#shorts` tag |
| YouTube Shorts homepage | `YouTube Shorts - Brave` | ✅ Yes | Starts with `YouTube Shorts` |
| Regular YouTube video | `Minecraft Tutorial - YouTube - Brave` | ✅ No | No `#shorts`, not Shorts page |
| YouTube homepage | `YouTube - Brave` | ✅ No | No `#shorts`, not Shorts page |
| YouTube search | `shorts tutorial - YouTube - Brave` | ✅ No | Word "shorts" without `#` is ignored |
| Google search for shorts | `shorts - Google - Brave` | ✅ No | Not a YouTube tab |
| Gmail | `Inbox - Gmail - Brave` | ✅ No | Not a YouTube tab |
| Any other website | `anything - Brave` | ✅ No | Not a YouTube tab |
| YouTube with hashtags (not Shorts) | `Zombies #edit #countryballs - YouTube - Brave` | ✅ No | No `#shorts` specifically |

The key insight: the `#shorts` hashtag is what separates a Shorts video from any other
YouTube video. YouTube itself puts `#shorts` in the browser tab title for every Shorts video.
Regular videos may have other hashtags like `#edit` or `#funny` but not `#shorts`.

---

## Optional: Enable Exact URL Detection (Recommended)

Title detection is reliable but not perfect — it depends on video creators tagging their
videos with `#shorts`. If a Shorts video has no `#shorts` tag in its title, it won't
be caught by Method B.

Method A (debug port) reads the **exact URL** like `youtube.com/shorts/abc123` which
is always present regardless of the video title. This catches 100% of Shorts.

To enable: follow the **Method A** setup steps above.

---

## Troubleshooting

**App opens but nothing is blocked**
Run `debug_test.py` while a Shorts tab is open. It prints exactly what the app can see.

**`ModuleNotFoundError`**
Run `pip install psutil pyautogui requests` in Command Prompt.

**Tab is not closing**
Make sure the browser window is in focus (not minimised) when Shorts plays.
The app only acts on the currently active window.

**App closes when I close the terminal**
Double-click the `.py` file instead of running from Command Prompt, or keep the
Command Prompt window open while using it.

---

## Supported Browsers

| Browser | Title Method | Debug Port Method |
|---|---|---|
| Brave | ✅ | ✅ (with flag) |
| Google Chrome | ✅ | ✅ (with flag) |
| Microsoft Edge | ✅ | ✅ (with flag) |
| Firefox | ✅ | ❌ (uses different protocol) |
| Opera | ✅ | ✅ (with flag) |