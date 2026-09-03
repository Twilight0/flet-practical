# Flet Practical Extension Suite

A unified, production-ready Flet extension suite bundling 9 essential device and system capabilities for **Mobile (Android & iOS)**, **Desktop (Linux, Windows, macOS)**, and **Web**:

1. 📋 **Clipboard**: Full cross-platform clipboard support (Text, HTML, raw images, and file paths).
2. 🔔 **Local & Persistent Notifications**: Trigger local and ongoing status bar notifications.
3. 💡 **Screen WakeLock**: Prevent the device display from sleeping during long tasks or audio playback.
4. 🎙️ **Edge Neural TTS**: High-quality speech synthesis using Microsoft's Edge neural voice engine (300+ voices).
5. 🚀 **Auto-Start on Boot**: Configure automatic app startup on device boot and system launch.
6. 💳 **In-App Purchases**: Manage Google Play & Apple App Store in-app billing, consumables, and subscriptions.
7. 📤 **Native Share Intent & File Opener**: Open the native OS Share Sheet (`ACTION_SEND`) and open files/folders with the default app (`ACTION_VIEW` via `open_filex` + `url_launcher`).
8. 🔄 **Background Service**: Keep the Python isolate alive after Home via Android ForegroundService.
9. 📥 **Receive Share Intent**: Receive incoming shares from other apps (text, URLs, images, videos) via Android share menu.

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

## Android Build Template (Cookiecutter Overlay)

`flet-practical` bundles 4 Android plugins that the stock `flet` template does not configure:
`receive_sharing_intent` (needs `compileSdk 37` + `SEND`/`SEND_MULTIPLE` intent-filters) and
`flutter_local_notifications` (needs `isCoreLibraryDesugaringEnabled` + `desugar_jdk_libs:2.1.4`).
`flet build apk` renders a `cookiecutter` project from `https://github.com/flet-dev/flet/releases/download/v0.86.5/flet-build-template.zip`
(`BaseBuildCommand.create_flutter_project()` → `cookiecutter(template=url, directory=dir, checkout=ref, extra_context=template_data)`),
cached in `~/.flet/cache/build-template/`, hashed via `HashStamp` — if you patch `build/` after `flet build`, the next `flet build` overwrites it. The overlay makes the patches **part of the template**, so `flet build` itself produces a correct `build/flutter`.

### What the overlay is

`flet-practical/templates/build/` is a **full copy** of `flet-build-template v0.86.5` (`build/cookiecutter.json`, `build/{{cookiecutter.out_dir}}/android/…`, `ios/…`, `pubspec.yaml` etc.) with a minimal diff:

* `android/app/build.gradle.kts:23` `compileSdk = 37` (was `flutter.compileSdkVersion` = 36 on Flutter 3.44.8)
* `android/app/build.gradle.kts:66` `isCoreLibraryDesugaringEnabled = true` + `135` `coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")`
* `android/app/src/main/AndroidManifest.xml:28` `singleTop → singleTask` + 8 `intent-filter`s for `receive_sharing_intent` (wrapped in `{% if _receive_share %}`).

Everything else (`pubspec.yaml`, `ios/`, `gradle.properties`, `mipmap`s) is upstream verbatim. You can modify any file in `templates/build/` — it is a normal `cookiecutter` template rendered with `{{ cookiecutter.* }}` (`template_data` includes your `pyproject.toml` as `cookiecutter.pyproject`).

### How to use

**Local dev (inside `flet-practical` repo or via path):**
```toml
# app/pyproject.toml
[tool.flet.template]
url = "/home/twilight/Development/flet_extensions/flet-practical/templates/build"
# no dir/ref needed — url already points to the template root (contains cookiecutter.json)
```

**From git (for teammates/CI, no local path):**
```toml
[tool.flet.template]
url = "https://github.com/Twilight0/flet-practical"
dir = "templates/build"   # subfolder inside the repo that holds cookiecutter.json
ref = "v0.3.1"            # tag/branch/commit — pin to flet-practical version
```

Then just:
```bash
uv run flet clean   # clears cached build/ so HashStamp re-renders from overlay
uv run flet build apk --arch arm64-v8a   # or: uv run python build_apk.py (now only does packaging, no manual patch)
```

`flet` will `git clone` the `flet-practical` repo at `ref`, `cd` into `templates/build`, render `{{cookiecutter.out_dir}}` → `build/flutter`, and `HashStamp` will cache `template_url+ref+dir+template_data`. Changing `ref` or `pyproject.toml`’s `receive_share` invalidates the cache.

### Toggling share intent-filters

By default `receive_share` is **enabled** (filters rendered) so `ReceiveShare` works out-of-the-box:
```xml
{% set _receive_share = cookiecutter.pyproject.get('tool', {}).get('flet', {}).get('android', {}).get('receive_share', True) %}
{% if _receive_share %} ...8 intent-filters... {% endif %}
```

* App **with** share sheet (InstaSave):
  ```toml
  [tool.flet.android]
  receive_share = true  # default, can omit
  ```
* App **without** `ReceiveShare` (e.g. TTS-only, no share sheet):
  ```toml
  [tool.flet.android]
  receive_share = false  # → manifest renders no SEND filters, app won't appear in Android share sheet
  ```

Permissions remain declarative via `tool.flet.android.permission` (already documented) — the template only adds the `Gradle`/`manifest` bits that `tool.flet` does not expose.

### Modifiable?

Yes — the overlay is a full template, not a patch file. Edit any `templates/build/{{cookiecutter.out_dir}}/…` file, commit, bump `ref`. `iOS` is not yet patched (priority later) — add `ios/Runner/Info.plist` / `Podfile` in same overlay when needed.

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

### 7. Native Share Intent & File Opener
```python
from flet_practical import Share

share = Share(page)  # pass page on mobile for native bridge, or Share() on desktop

# Share text or URL
await share.share_text("Check this out: https://flet.dev", subject="Flet App")

# Share files
await share.share_files(["/path/to/invoice.pdf"])

# Open a file with the default app (Android: FileProvider + open_filex, Desktop: xdg-open/open/startfile)
await share.open_file("/storage/emulated/0/Download/video.mp4")  # -> Gallery / VLC / etc.
# returns True if handler found (Android: OpenResult type == "done")

# Open a folder in the system file manager (Android: Uri.file + url_launcher + SAF fallback)
await share.open_folder("/storage/emulated/0/Download")  # -> Files / Samsung My Files
# or open parent folder of a file:
await share.open_folder("/storage/emulated/0/Pictures/InstaSave/image.jpg")
```


### 8. Background Service
Keep the Python isolate alive after the user returns to the Android desktop via a `ForegroundService` with an ongoing notification. `Wakelock` alone only prevents screen sleep while in foreground.

```python
from flet_practical import BackgroundService

bg = BackgroundService(page)

# One-time: disable battery optimization (Xiaomi/Samsung will still kill otherwise)
if not await bg.is_ignoring_battery_optimizations():
    await bg.request_ignore_battery_optimization()
    # fallback: await bg.open_ignore_battery_optimization_settings()

# Keep running after Home
await bg.start(title="MyApp", text="Running in background…")
# ... long asyncio work / download queue keeps running ...
# await bg.is_running() -> bool
# await bg.restart()
await bg.stop()
```

Battery helpers live on the same `BackgroundService`:
`is_ignoring_battery_optimizations()` / `request_ignore_battery_optimization()` / `open_ignore_battery_optimization_settings()` — call from your `SettingsView` one-time toggle or auto-prompt before `start()`.

> **Why does the Python thread stop on Home?** On APK the Python isolate lives inside the `Activity` process — `Home` → `onPause()/onStop()` → without a `ForegroundService` Android kills the `FlutterEngine` (and thus the Python bridge) in seconds. This is expected Android behavior, not a Flet bug. `BackgroundService` promotes the process via `FOREGROUND_SERVICE_DATA_SYNC` + `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` + ongoing notification (`flutter_foreground_task 11.0.1`).

### 9. Receive Share Intent
Receive incoming shares from other apps when your app appears in Android's system share sheet (`ACTION_SEND` for `text/plain`, `image/*`, `video/*`). Replaces the native `ShareReceiverActivity`.

```python
from flet_practical import ReceiveShare

async def handle_share(files): # List[Dict] {path, type, mimeType, thumbnail, duration, message}
    for f in files:
        print(f["path"], f["type"]) # e.g. "https://..." text or "/tmp/.../shared.jpg" image
        # InstaSave: auto-fill download bar -> download_view.url_input.value = f["path"]

receive = ReceiveShare(page, on_share=handle_share)
# Pull initial share if app was launched via share
files = await receive.get_initial_share()
# await receive.reset() # clear after handling
```

The `ReceiveShare` service (`practical_receive_share`) listens via `receive_sharing_intent` (`getInitialMedia()` + `getMediaStream()` → `control.triggerEvent("share")`). Works for `text`/`url`/`image`/`video`/`file`.

---

## Examples

Run any demo independently:

```bash
uv run python examples/main.py             # Main Hub (All 9 Features)
uv run python examples/01_clipboard.py     # Clipboard demo
uv run python examples/02_notifications.py # Notifications demo
uv run python examples/03_wakelock.py      # WakeLock demo
uv run python examples/04_tts.py           # TTS demo
uv run python examples/05_autostart.py     # AutoStart demo
uv run python examples/06_iap.py           # In-App Purchases demo
uv run python examples/07_share.py         # Native Share Intent demo
uv run python examples/08_background.py    # Background Service demo
uv run python examples/09_receive_share.py # Receive Share Intent demo
```

---

## License

MIT License.
