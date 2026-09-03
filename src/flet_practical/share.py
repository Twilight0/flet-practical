import asyncio
import os
import shutil
import sys
from typing import Any, List, Optional

import flet as ft


@ft.control("practical_share")
class PracticalShare(ft.Service):
    async def share_text(self, text: str, subject: Optional[str] = None):
        return await self._invoke_method("share_text", arguments={"text": text, "subject": subject})

    async def share_files(self, paths: List[str], text: Optional[str] = None, subject: Optional[str] = None):
        return await self._invoke_method("share_files", arguments={"paths": paths, "text": text, "subject": subject})

    async def share_uri(self, uri: str):
        return await self._invoke_method("share_uri", arguments={"uri": uri})

    async def open_file(self, path: str):
        return await self._invoke_method("open_file", arguments={"path": path})

    async def open_folder(self, path: str):
        return await self._invoke_method("open_folder", arguments={"path": path})


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
        self._service: Optional[PracticalShare] = None
        self._service_registered: bool = False

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

    def _ensure_service(self) -> Optional[PracticalShare]:
        if self._service_registered and self._service:
            return self._service
        current_page = self.page
        if not current_page:
            return None
        try:
            services = getattr(current_page, "services", None)
            if services is not None:
                for s in services:
                    if isinstance(s, PracticalShare):
                        self._service = s
                        self._service_registered = True
                        return self._service
                self._service = PracticalShare()
                services.append(self._service)
                self._service_registered = True
                # Ensure page updates so flutter extension is mounted
                if hasattr(current_page, "update"):
                    try:
                        current_page.update()
                    except Exception:
                        pass
                return self._service
        except Exception:
            pass
        return None

    def _is_mobile(self) -> bool:
        current_page = self.page
        if current_page and hasattr(current_page, "platform"):
            try:
                p = current_page.platform
                # flet PagePlatform enum has is_mobile() in newer versions
                if hasattr(p, "is_mobile") and callable(getattr(p, "is_mobile")):
                    try:
                        if p.is_mobile():
                            return True
                    except Exception:
                        pass
                s = str(p).lower()
                if "android" in s or "ios" in s:
                    return True
            except Exception:
                pass
        # Fallback env checks for Android
        return "ANDROID_ARGUMENT" in os.environ or "ANDROID_ROOT" in os.environ

    async def share_text(self, text: str, subject: Optional[str] = None) -> bool:
        """
        Open the native system share sheet to share plain text or URLs.
        """
        if not text:
            return False

        # Mobile: delegate to native share sheet via practical_share
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    res = await svc.share_text(text, subject=subject)
                    # Flutter returns {"status": "...", "raw": ...}
                    if isinstance(res, dict):
                        status = str(res.get("status", "")).lower()
                        # success/dismissed both mean sheet opened; unavailable/error means failed
                        return status not in ("unavailable", "error", "")
                    return bool(res)
                except Exception:
                    pass

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

        # Mobile: delegate to native share sheet via practical_share
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    res = await svc.share_files(valid_paths, text=text, subject=subject)
                    if isinstance(res, dict):
                        status = str(res.get("status", "")).lower()
                        return status not in ("unavailable", "error", "")
                    return bool(res)
                except Exception:
                    pass

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
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    res = await svc.share_uri(uri)
                    if isinstance(res, dict):
                        status = str(res.get("status", "")).lower()
                        return status not in ("unavailable", "error", "")
                    return bool(res)
                except Exception:
                    pass
        return await self.share_text(uri)

    async def open_file(self, path: str) -> bool:
        """
        Open a file in the system's default application.
        On Android: Uses native FileProvider Intent via OpenFilex.
        On Desktop: Uses xdg-open / os.startfile / open.
        """
        if not path or not os.path.exists(path):
            return False
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    res = await svc.open_file(path)
                    if isinstance(res, dict) and str(res.get("type", "")).lower() in ("done", "success"):
                        return True
                except Exception as e:
                    print(f"[Share.open_file] Mobile open_file error: {e}")
        try:
            if sys.platform.startswith("linux") and shutil.which("xdg-open"):
                import subprocess
                subprocess.Popen(["xdg-open", path])
                return True
            elif sys.platform == "win32":
                os.startfile(path)
                return True
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", path])
                return True
        except Exception:
            pass
        return False

    async def open_folder(self, path: str) -> bool:
        """
        Open a folder in the system file manager.
        On Android: Uses Uri.file + url_launcher (externalApplication) with SAF fallback.
        On Desktop: Opens file manager.
        """
        if not path:
            return False
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    res = await svc.open_folder(path)
                    if isinstance(res, dict):
                        if res.get("status") == "success":
                            return True
                        # fallback: treat no_handler/error as failure so desktop fallback not triggered on mobile
                        return False
                    # if service returns truthy non-dict, consider success
                    if res:
                        return True
                except Exception as e:
                    print(f"[Share.open_folder] Mobile open_folder error: {e}")
                return False
        try:
            folder = path if os.path.isdir(path) else os.path.dirname(path)
            if sys.platform.startswith("linux") and shutil.which("xdg-open"):
                import subprocess
                subprocess.Popen(["xdg-open", folder])
                return True
            elif sys.platform == "win32":
                os.startfile(folder)
                return True
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", folder])
                return True
        except Exception:
            pass
        return False

