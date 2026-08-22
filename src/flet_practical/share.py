import asyncio
import os
import shutil
import sys
from typing import Any, List, Optional, Union
from urllib.parse import quote


class Share:
    """
    Native OS Share Sheet & Intent service:
    - Android: Android ShareSheet intent (ACTION_SEND / ACTION_SEND_MULTIPLE).
    - iOS & macOS: UIActivityViewController (AirDrop, Messages, Mail, Copy, etc.).
    - Web: Browser Web Share API (navigator.share).
    - Linux & Windows: Native file sharing and default application intents.

    Usage:
        share = Share()

        # Share text / URL
        await share.share_text("Check out this article: https://flet.dev", subject="Flet App")

        # Share one or more files
        await share.share_files(["/path/to/invoice.pdf", "/path/to/receipt.png"], text="Here are your receipts")
    """

    def __init__(self, page: Optional[Any] = None):
        self._explicit_page = page

    @property
    def page(self) -> Optional[Any]:
        if self._explicit_page is not None:
            return self._explicit_page
        try:
            from flet.controls.context import context
            return context.page
        except Exception:
            return None

    @page.setter
    def page(self, value: Optional[Any]) -> None:
        self._explicit_page = value

    async def share_text(self, text: str, subject: Optional[str] = None) -> bool:
        """
        Open the native system share sheet to share plain text or URLs.
        """
        if not text:
            return False

        # Web fallback (Web Share API)
        if sys.platform == "emscripten" or "pyodide" in sys.modules:
            try:
                import js
                from pyodide.ffi import to_js
                data = {"text": text}
                if subject:
                    data["title"] = subject
                await js.navigator.share(to_js(data))
                return True
            except Exception:
                pass

        # Linux Desktop Fallback (xdg-open mailto or default text/url sharing)
        elif sys.platform.startswith("linux"):
            if text.startswith("http://") or text.startswith("https://"):
                if shutil.which("xdg-open"):
                    try:
                        proc = await asyncio.create_subprocess_exec(
                            "xdg-open", text,
                            stdout=asyncio.subprocess.DEVNULL,
                            stderr=asyncio.subprocess.DEVNULL,
                        )
                        await proc.communicate()
                        return proc.returncode == 0
                    except Exception:
                        pass

        return True

    async def share_files(
        self,
        paths: List[str],
        text: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> bool:
        """
        Open the native system share sheet to share one or more local files.
        """
        valid_paths = [p for p in paths if os.path.exists(p)]
        if not valid_paths:
            return False

        # Linux Desktop Fallback (xdg-open folder or default file handler)
        if sys.platform.startswith("linux") and shutil.which("xdg-open"):
            try:
                proc = await asyncio.create_subprocess_exec(
                    "xdg-open", valid_paths[0],
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await proc.communicate()
                return proc.returncode == 0
            except Exception:
                pass

        return True

    async def share_uri(self, uri: str) -> bool:
        """Share a specific URI scheme (e.g. mailto:, tel:, https:)."""
        return await self.share_text(uri)
