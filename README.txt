# YouTube Shorts Blocker — Windows Prototype

Automatically closes browser tabs when YouTube Shorts is detected.

---

## FILES

| File | What it does |
|---|---|
| `shorts_blocker.py` | The brain — detects Shorts and closes the tab |
| `shorts_blocker_gui.py` | The visual app — run this one |

---

## SETUP (One Time)

### Step 1 — Install Python
Download from: https://python.org/downloads
- During install, CHECK the box that says "Add Python to PATH"

### Step 2 — Install required library
Open Command Prompt and run:
```
pip install pyautogui psutil
```

### Step 3 — Run the app
Double-click `shorts_blocker_gui.py`
OR open Command Prompt in the folder and run:
```
python shorts_blocker_gui.py
```

---

## HOW TO USE

1. Run the app
2. Click **TURN ON**
3. Open YouTube in Chrome / Firefox / Edge
4. Go to any Shorts video
5. The tab closes automatically!

---

## HOW IT DETECTS SHORTS

It reads the **browser window title bar**. When you're on a Shorts video,
the title contains the word "Shorts" — the app sees this and closes the tab.

Example title it catches:
- "YouTube Shorts - Google Chrome"
- "#shorts - YouTube"

---

## SUPPORTED BROWSERS

- Google Chrome
- Mozilla Firefox
- Microsoft Edge
- Opera
- Brave

---

## NOTES

- Both files must be in the SAME folder
- The app only acts when your browser is the active window
- It does NOT read your browsing history or collect any data
- Works fully offline
