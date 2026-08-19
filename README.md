# Flet Clipboard Extension

A cross-platform Flet extension providing full device clipboard access for **Desktop (Linux, Windows, macOS)**, **Mobile (Android, iOS)**, and **Web**.

Powered under the hood by Flutter's [`pasteboard`](https://pub.dev/packages/pasteboard) plugin.

---

## Features

- 📝 **Plain Text**: Read and write text to the system clipboard.
- 🖼️ **Images**: Read and write image data (raw bytes and Base64 strings).
- 🌐 **Rich Text / HTML**: Read and write formatted HTML snippets.
- 📁 **File Paths**: Retrieve lists of copied file paths.
- 🧹 **Clear**: Clear clipboard content with one call.
- ⚡ **Lightweight & Async**: Clean Python `async`/`await` API.

---

## Installation

```bash
pip install flet-clipboard
```

---

## Quickstart

```python
import flet as ft
from flet_clipboard import Clipboard

async def main(page: ft.Page):
    # 1. Attach Clipboard control to page overlay
    clipboard = Clipboard()
    page.overlay.append(clipboard)
    page.update()

    # 2. Write Text
    await clipboard.set_text("Hello from Flet!")

    # 3. Read Text
    text = await clipboard.get_text()
    print("Clipboard content:", text)

    # 4. Check if clipboard has content
    has_text = await clipboard.has_text()

    # 5. Read Images
    image_bytes = await clipboard.get_image()
    if image_bytes:
        print(f"Clipboard image size: {len(image_bytes)} bytes")

    # 6. Read Files
    files = await clipboard.get_files()
    print("Copied files:", files)

ft.app(target=main)
```

---

## API Reference

### `Clipboard`

| Method | Parameters | Returns | Description |
| :--- | :--- | :--- | :--- |
| `get_text()` | — | `Optional[str]` | Reads plain text from clipboard. |
| `set_text(text)` | `text: str` | `bool` | Writes plain text to clipboard. |
| `has_text()` | — | `bool` | Returns `True` if clipboard has text. |
| `get_html()` | — | `Optional[str]` | Reads HTML formatted text. |
| `set_html(html, text)` | `html: str, text: Optional[str]` | `bool` | Writes HTML formatted text. |
| `get_image()` | — | `Optional[bytes]` | Reads image as raw bytes (PNG/JPEG). |
| `get_image_base64()` | — | `Optional[str]` | Reads image as Base64 string. |
| `set_image(image)` | `image: Union[bytes, str]` | `bool` | Writes image bytes or Base64. |
| `has_image()` | — | `bool` | Returns `True` if clipboard has an image. |
| `get_files()` | — | `List[str]` | Returns list of copied file paths. |
| `set_files(files)` | `files: List[str]` | `bool` | Writes list of file paths. |
| `clear()` | — | `bool` | Clears clipboard contents. |

---

## License

MIT License.
