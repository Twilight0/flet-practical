import base64
from typing import Any, List, Optional, Union
import flet as ft
from flet.controls.base_control import control


@control("flet_clipboard")
class Clipboard(ft.Control):
    """
    Flet Clipboard Control.
    Enables reading and writing device clipboard data:
    - Plain Text
    - HTML / Rich Text
    - Images (raw bytes and base64)
    - File paths

    Usage:
        clipboard = Clipboard()
        page.overlay.append(clipboard)
        page.update()

        text = await clipboard.get_text()
        await clipboard.set_text("Hello from Flet!")
    """

    def __init__(
        self,
        ref: Optional[ft.Ref] = None,
        data: Any = None,
    ):
        super().__init__(ref=ref, data=data)

    async def get_text(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get plain text content from the clipboard."""
        return await self._invoke_method("get_text", timeout=timeout)

    async def set_text(self, text: str, timeout: Optional[float] = None) -> bool:
        """Write plain text content to the clipboard."""
        res = await self._invoke_method("set_text", {"text": text}, timeout=timeout)
        return bool(res)

    async def get_html(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get HTML formatted text from the clipboard."""
        return await self._invoke_method("get_html", timeout=timeout)

    async def set_html(self, html: str, text: Optional[str] = "", timeout: Optional[float] = None) -> bool:
        """Write HTML formatted text to the clipboard with fallback plain text."""
        res = await self._invoke_method("set_html", {"html": html, "text": text or ""}, timeout=timeout)
        return bool(res)

    async def get_image(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """Get image from the clipboard as raw PNG/JPEG bytes."""
        b64 = await self.get_image_base64(timeout=timeout)
        if b64:
            return base64.b64decode(b64)
        return None

    async def get_image_base64(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get image from the clipboard as a base64 encoded string."""
        return await self._invoke_method("get_image", timeout=timeout)

    async def set_image(self, image: Union[bytes, str], timeout: Optional[float] = None) -> bool:
        """
        Write image bytes or base64 string to the clipboard.
        """
        if isinstance(image, bytes):
            b64 = base64.b64encode(image).decode("utf-8")
        else:
            b64 = image
        res = await self._invoke_method("set_image", {"image_base64": b64}, timeout=timeout)
        return bool(res)

    async def get_files(self, timeout: Optional[float] = None) -> List[str]:
        """Get list of file paths currently copied to the clipboard."""
        res = await self._invoke_method("get_files", timeout=timeout)
        if isinstance(res, list):
            return [str(f) for f in res]
        return []

    async def set_files(self, files: List[str], timeout: Optional[float] = None) -> bool:
        """Write a list of file paths to the clipboard."""
        res = await self._invoke_method("set_files", {"files": files}, timeout=timeout)
        return bool(res)

    async def has_text(self, timeout: Optional[float] = None) -> bool:
        """Check if the clipboard contains non-empty text."""
        res = await self._invoke_method("has_text", timeout=timeout)
        return bool(res)

    async def has_image(self, timeout: Optional[float] = None) -> bool:
        """Check if the clipboard contains an image."""
        res = await self._invoke_method("has_image", timeout=timeout)
        return bool(res)

    async def clear(self, timeout: Optional[float] = None) -> bool:
        """Clear clipboard content."""
        res = await self._invoke_method("clear", timeout=timeout)
        return bool(res)
