# Flet Practical Extension Suite

A unified, production-ready Flet extension suite bundling 7 essential device and system capabilities for **Mobile (Android & iOS)**, **Desktop (Linux, Windows, macOS)**, and **Web**:

1. 📋 **Clipboard**: Full cross-platform clipboard support (Text, HTML, raw images, and file paths).
2. 🔔 **Local & Persistent Notifications**: Trigger local and ongoing status bar notifications.
3. 💡 **Screen WakeLock**: Prevent the device display from sleeping during long tasks or audio playback.
4. 🎙️ **Edge Neural TTS**: High-quality speech synthesis using Microsoft's Edge neural voice engine (300+ voices).
5. 🚀 **Auto-Start on Boot**: Configure automatic app startup on device boot and system launch.
6. 💳 **In-App Purchases**: Manage Google Play & Apple App Store in-app billing, consumables, and subscriptions.
7. 📤 **Native Share Intent**: Open the native OS Share Sheet (Android `ACTION_SEND`, iOS `UIActivityViewController`, Web Share API).

---

## Installation

**From PyPI (once published):**
```bash
pip install flet-practical
# or
uv add flet-practical
```

**From GitHub (no PyPI needed — PEP 508 direct reference, works with `uv` and `flet build`):**
```toml
# in your app's pyproject.toml
[project]
dependencies = [
  "flet-practical @ git+https://github.com/Twilight0/flet-practical.git",
  "flet>=0.86.5",
]
```
```bash
# then
uv sync
# or with pip
pip install "flet-practical @ git+https://github.com/Twilight0/flet-practical.git"

# pin to a tag / branch / commit:
# "flet-practical @ git+https://github.com/Twilight0/flet-practical.git@v0.1.0"
# "flet-practical @ git+https://github.com/Twilight0/flet-practical.git@main"
```

---

## Modules Overview

### 1. Clipboard
```python
from flet_practical import Clipboard

clipboard = Clipboard()
await clipboard.set_text("Hello!")
text = await clipboard.get_text()
img_bytes = await clipboard.get_image()
```

### 2. Local & Persistent Notifications
```python
from flet_practical import Notifications

# on_click fires when the notification body is tapped (payload is returned)
notifications = Notifications(on_click=lambda payload: print(f"Tapped: {payload}"))

await notifications.request_permissions()

# Standard alert
await notifications.show(
    id=1,
    title="Download Finished",
    body="Your file has been saved.",
    payload="download:123",  # returned to on_click
)

# Persistent / ongoing (stays in Android status bar until cancelled)
await notifications.show(
    id=2,
    title="Sync Service",
    body="Synchronizing files in background...",
    ongoing=True,
)

# Clickable action buttons (Linux desktop: notify-send -A; mobile: taps return payload)
# on_action fires with the action key ("summarize", "speak", etc.)
await notifications.show(
    id=3,
    title="Clipboard: text copied",
    body="Long article copied — summarize or listen?",
    actions=[
        ("summarize", "Summarize"),
        ("speak", "Speak"),
        ("search", "Search"),
    ],
    on_action=lambda action_id: print(f"Action clicked: {action_id}"),
    payload="clip:summarize",  # fallback if body tapped
)

# Cancel
await notifications.cancel(2)
await notifications.cancel_all()
```

### 3. Screen WakeLock
```python
from flet_practical import WakeLock

wakelock = WakeLock()
await wakelock.enable()   # Keep screen awake
await wakelock.disable()  # Allow normal sleep
```

### 4. Neural Text-to-Speech
```python
from flet_practical import TtsService

tts = TtsService(voice="en-US-JennyNeural")
await tts.speak("Welcome to Flet Practical!", play_immediately=True)
```

### 5. Auto-Start on Boot
```python
from flet_practical import AutoStart

autostart = AutoStart(app_name="MyApp")
await autostart.enable()
is_on = await autostart.is_enabled()
```

### 6. In-App Purchases
```python
from flet_practical import InAppPurchase

def on_purchase(event):
    print("Purchased:", event["product_id"])

iap = InAppPurchase(on_purchase=on_purchase)
products = await iap.get_products(["pro_monthly"])
await iap.buy("pro_monthly")
```

### 7. Native Share Intent
```python
from flet_practical import Share

share = Share()

# Share text or URL
await share.share_text("Check this out: https://flet.dev", subject="Flet App")

# Share files
await share.share_files(["/path/to/invoice.pdf"])
```

---

## Examples

Run any demo independently:

```bash
uv run python examples/main.py             # Main Hub (All 7 Features)
uv run python examples/01_clipboard.py     # Clipboard demo
uv run python examples/02_notifications.py # Notifications demo
uv run python examples/03_wakelock.py      # WakeLock demo
uv run python examples/04_tts.py           # TTS demo
uv run python examples/05_autostart.py     # AutoStart demo
uv run python examples/06_iap.py           # In-App Purchases demo
uv run python examples/07_share.py         # Native Share Intent demo
```

---

## License

MIT License.
