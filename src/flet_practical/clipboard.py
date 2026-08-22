import asyncio
import base64
import os
import shutil
import sys
from typing import Any, List, Optional, Union
from urllib.parse import unquote, urlparse


class Clipboard:
    """
    Universal cross-platform device clipboard service.
    - Android & iOS: Native mobile clipboard bridge via Flutter engine.
    - Desktop (Linux, macOS, Windows): Direct OS pipe/Win32 engine.
    - Web (Pyodide / WASM): Browser navigator.clipboard API.
    """

    def __init__(self, page: Optional[Any] = None):
        self._explicit_page = page
        self._builtin_service: Optional[Any] = None
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

    def _ensure_mobile_service(self) -> None:
        if self._service_registered:
            return

        current_page = self.page
        if not current_page:
            return

        try:
            from flet.controls.services.clipboard import Clipboard as FletClipboardService

            services = getattr(current_page, "services", None)
            if services is not None:
                for s in services:
                    if isinstance(s, FletClipboardService):
                        self._builtin_service = s
                        self._service_registered = True
                        return

                self._builtin_service = FletClipboardService()
                services.append(self._builtin_service)
                self._service_registered = True
                if hasattr(current_page, "update"):
                    try:
                        current_page.update()
                    except Exception:
                        pass
        except Exception:
            pass

    def _is_mobile(self) -> bool:
        current_page = self.page
        if current_page and hasattr(current_page, "platform") and current_page.platform:
            try:
                p = current_page.platform
                if hasattr(p, "is_mobile") and p.is_mobile():
                    return True
                if str(p).lower() in ("android", "ios", "pageplatform.android", "pageplatform.ios"):
                    return True
            except Exception:
                pass
        return "ANDROID_ARGUMENT" in os.environ or "ANDROID_ROOT" in os.environ or "ANDROID_BOOTLOGO" in os.environ

    def _is_web(self) -> bool:
        current_page = self.page
        if current_page and getattr(current_page, "web", False):
            return True
        return sys.platform == "emscripten" or "pyodide" in sys.modules

    async def get_text(self) -> Optional[str]:
        """Get plain text from clipboard."""
        if self._is_web():
            return await self._get_text_web()
        elif self._is_mobile():
            return await self._get_text_mobile()
        elif sys.platform.startswith("linux"):
            return await self._get_text_linux()
        elif sys.platform == "darwin":
            return await self._get_text_macos()
        elif sys.platform == "win32":
            return await self._get_text_windows()
        return None

    async def set_text(self, text: str) -> bool:
        """Write plain text to clipboard."""
        if self._is_web():
            return await self._set_text_web(text)
        elif self._is_mobile():
            return await self._set_text_mobile(text)
        elif sys.platform.startswith("linux"):
            return await self._set_text_linux(text)
        elif sys.platform == "darwin":
            return await self._set_text_macos(text)
        elif sys.platform == "win32":
            return await self._set_text_windows(text)
        return False

    async def has_text(self) -> bool:
        text = await self.get_text()
        return text is not None and len(text.strip()) > 0

    async def get_html(self) -> Optional[str]:
        """Get HTML formatted text."""
        if sys.platform.startswith("linux") and not self._is_mobile():
            return await self._run_command_output(
                ["xclip", "-selection", "clipboard", "-t", "text/html", "-o"],
                fallback_cmd=["wl-paste", "-t", "text/html"],
            )
        return None

    async def set_html(self, html: str, text: Optional[str] = "") -> bool:
        """Write HTML formatted text."""
        if sys.platform.startswith("linux") and not self._is_mobile():
            if shutil.which("xclip"):
                return await self._run_command_input(
                    ["xclip", "-selection", "clipboard", "-t", "text/html", "-i"],
                    input_data=html.encode("utf-8"),
                )
            elif shutil.which("wl-copy"):
                return await self._run_command_input(
                    ["wl-copy", "-t", "text/html"],
                    input_data=html.encode("utf-8"),
                )
        return await self.set_text(text or html)

    async def get_image(self) -> Optional[bytes]:
        """Get raw image bytes."""
        if self._is_mobile():
            return await self._get_image_mobile()
        elif sys.platform.startswith("linux"):
            png = await self._run_command_bytes(
                ["xclip", "-selection", "clipboard", "-t", "image/png", "-o"],
                fallback_cmd=["wl-paste", "-t", "image/png"],
            )
            if png:
                return png
            return await self._run_command_bytes(
                ["xclip", "-selection", "clipboard", "-t", "image/jpeg", "-o"],
                fallback_cmd=["wl-paste", "-t", "image/jpeg"],
            )
        elif sys.platform == "darwin" and shutil.which("pngpaste"):
            try:
                proc = await asyncio.create_subprocess_exec(
                    "pngpaste", "-",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                stdout, _ = await proc.communicate()
                return stdout if stdout else None
            except Exception:
                return None
        return None

    async def get_image_base64(self) -> Optional[str]:
        raw = await self.get_image()
        if raw:
            return base64.b64encode(raw).decode("utf-8")
        return None

    async def set_image(self, image: Union[bytes, str]) -> bool:
        """Write image bytes or base64 string."""
        raw_bytes = base64.b64decode(image) if isinstance(image, str) else image
        if self._is_mobile():
            return await self._set_image_mobile(raw_bytes)
        elif sys.platform.startswith("linux"):
            if shutil.which("xclip"):
                return await self._run_command_input(
                    ["xclip", "-selection", "clipboard", "-t", "image/png", "-i"],
                    input_data=raw_bytes,
                )
            elif shutil.which("wl-copy"):
                return await self._run_command_input(
                    ["wl-copy", "-t", "image/png"],
                    input_data=raw_bytes,
                )
        return False

    async def has_image(self) -> bool:
        img = await self.get_image()
        return img is not None and len(img) > 0

    async def get_files(self) -> List[str]:
        """Get copied file path list."""
        if self._is_mobile():
            self._ensure_mobile_service()
            if self._builtin_service:
                try:
                    return await self._builtin_service.get_files()
                except Exception:
                    pass

        if sys.platform.startswith("linux") and not self._is_mobile():
            uri_text = await self._run_command_output(
                ["xclip", "-selection", "clipboard", "-t", "text/uri-list", "-o"],
                fallback_cmd=["wl-paste", "-t", "text/uri-list"],
            )
            if uri_text:
                paths = []
                for line in uri_text.strip().splitlines():
                    line = line.strip()
                    if line.startswith("file://"):
                        parsed = urlparse(line)
                        path = unquote(parsed.path)
                        if os.path.exists(path):
                            paths.append(path)
                    elif os.path.exists(line):
                        paths.append(line)
                return paths
        return []

    async def set_files(self, files: List[str]) -> bool:
        """Write list of file paths."""
        valid_files = [f for f in files if os.path.exists(f)]
        if not valid_files:
            return False

        if sys.platform.startswith("linux") and not self._is_mobile():
            uri_list = "\r\n".join([f"file://{os.path.abspath(f)}" for f in valid_files]) + "\r\n"
            if shutil.which("xclip"):
                return await self._run_command_input(
                    ["xclip", "-selection", "clipboard", "-t", "text/uri-list", "-i"],
                    input_data=uri_list.encode("utf-8"),
                )
            elif shutil.which("wl-copy"):
                return await self._run_command_input(
                    ["wl-copy", "-t", "text/uri-list"],
                    input_data=uri_list.encode("utf-8"),
                )
        return False

    async def clear(self) -> bool:
        """Clear clipboard contents."""
        return await self.set_text("")

    async def _get_text_mobile(self) -> Optional[str]:
        self._ensure_mobile_service()
        if self._builtin_service:
            try:
                return await self._builtin_service.get()
            except Exception:
                pass
        return None

    async def _set_text_mobile(self, text: str) -> bool:
        self._ensure_mobile_service()
        if self._builtin_service:
            try:
                await self._builtin_service.set(text)
                return True
            except Exception:
                pass
        return False

    async def _get_image_mobile(self) -> Optional[bytes]:
        self._ensure_mobile_service()
        if self._builtin_service:
            try:
                return await self._builtin_service.get_image()
            except Exception:
                pass
        return None

    async def _set_image_mobile(self, image_bytes: bytes) -> bool:
        self._ensure_mobile_service()
        if self._builtin_service:
            try:
                await self._builtin_service.set_image(image_bytes)
                return True
            except Exception:
                pass
        return False

    async def _get_text_linux(self) -> Optional[str]:
        if shutil.which("xclip"):
            return await self._run_command_output(["xclip", "-selection", "clipboard", "-o"])
        elif shutil.which("wl-paste"):
            return await self._run_command_output(["wl-paste", "--no-newline"])
        elif shutil.which("xsel"):
            return await self._run_command_output(["xsel", "-b", "-o"])
        return None

    async def _set_text_linux(self, text: str) -> bool:
        data = text.encode("utf-8")
        if shutil.which("xclip"):
            return await self._run_command_input(["xclip", "-selection", "clipboard", "-i"], data)
        elif shutil.which("wl-copy"):
            return await self._run_command_input(["wl-copy"], data)
        elif shutil.which("xsel"):
            return await self._run_command_input(["xsel", "-b", "-i"], data)
        return False

    async def _get_text_macos(self) -> Optional[str]:
        if shutil.which("pbpaste"):
            return await self._run_command_output(["pbpaste"])
        return None

    async def _set_text_macos(self, text: str) -> bool:
        if shutil.which("pbcopy"):
            return await self._run_command_input(["pbcopy"], text.encode("utf-8"))
        return False

    async def _get_text_windows(self) -> Optional[str]:
        try:
            import ctypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            if not user32.OpenClipboard(None):
                return None
            try:
                CF_UNICODETEXT = 13
                h_mem = user32.GetClipboardData(CF_UNICODETEXT)
                if not h_mem:
                    return None
                kernel32.GlobalLock.restype = ctypes.c_void_p
                p_mem = kernel32.GlobalLock(h_mem)
                if not p_mem:
                    return None
                try:
                    return ctypes.c_wchar_p(p_mem).value
                finally:
                    kernel32.GlobalUnlock(h_mem)
            finally:
                user32.CloseClipboard()
        except Exception:
            return None

    async def _set_text_windows(self, text: str) -> bool:
        try:
            import ctypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            if not user32.OpenClipboard(None):
                return False
            try:
                user32.EmptyClipboard()
                CF_UNICODETEXT = 13
                GMEM_MOVEABLE = 0x0002
                data = (text + "\0").encode("utf-16le")
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
                if not h_mem:
                    return False
                kernel32.GlobalLock.restype = ctypes.c_void_p
                p_mem = kernel32.GlobalLock(h_mem)
                if not p_mem:
                    return False
                ctypes.memmove(p_mem, data, len(data))
                kernel32.GlobalUnlock(h_mem)
                user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                return True
            finally:
                user32.CloseClipboard()
        except Exception:
            return False

    async def _get_text_web(self) -> Optional[str]:
        try:
            import js
            promise = js.navigator.clipboard.readText()
            return str(await promise)
        except Exception:
            return None

    async def _set_text_web(self, text: str) -> bool:
        try:
            import js
            promise = js.navigator.clipboard.writeText(text)
            await promise
            return True
        except Exception:
            return False

    async def _run_command_output(
        self,
        primary_cmd: List[str],
        fallback_cmd: Optional[List[str]] = None,
    ) -> Optional[str]:
        cmd = primary_cmd if shutil.which(primary_cmd[0]) else (fallback_cmd if fallback_cmd and shutil.which(fallback_cmd[0]) else None)
        if not cmd:
            return None
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0 and stdout:
                return stdout.decode("utf-8", errors="replace")
        except Exception:
            pass
        return None

    async def _run_command_bytes(
        self,
        primary_cmd: List[str],
        fallback_cmd: Optional[List[str]] = None,
    ) -> Optional[bytes]:
        cmd = primary_cmd if shutil.which(primary_cmd[0]) else (fallback_cmd if fallback_cmd and shutil.which(fallback_cmd[0]) else None)
        if not cmd:
            return None
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0 and stdout:
                return stdout
        except Exception:
            pass
        return None

    async def _run_command_input(self, cmd: List[str], input_data: bytes) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate(input=input_data)
            return proc.returncode == 0
        except Exception:
            return False
