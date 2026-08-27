import sys
from pathlib import Path
from typing import Any, Optional

import flet as ft


@ft.control("practical_autostart")
class PracticalAutostart(ft.Service):
    async def enable(self) -> bool:
        return await self._invoke_method("enable")

    async def disable(self) -> bool:
        return await self._invoke_method("disable")

    async def is_enabled(self) -> bool:
        return await self._invoke_method("is_enabled")


class AutoStart:
    """
    Manage auto-start on device boot / system startup:
    - Android: Boot completed receiver service (launch_at_startup).
    - iOS: handled natively (no explicit API in this extension).
    - Linux (Desktop): XDG autostart desktop entry (~/.config/autostart).
    - Windows / macOS (Desktop): best-effort no-op (registry / LaunchAgents not wired).

    Usage:
        autostart = AutoStart(app_name="MyFletApp", page=page)

        await autostart.enable()
        is_on = await autostart.is_enabled()
    """

    def __init__(
        self,
        app_name: str = "FletApp",
        app_path: Optional[str] = None,
        page: Optional[Any] = None,
    ):
        self.app_name = app_name
        self.app_path = app_path or sys.executable
        self._explicit_page = page
        self._service: Optional[PracticalAutostart] = None
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

    def _is_mobile(self) -> bool:
        p = getattr(self.page, "platform", None) if self.page else None
        return p in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, "android", "ios")

    def _ensure_service(self) -> Optional[PracticalAutostart]:
        if self._service_registered and self._service:
            return self._service

        current_page = self.page
        if not current_page:
            return None

        try:
            services = getattr(current_page, "services", None)
            if services is not None:
                for s in services:
                    if isinstance(s, PracticalAutostart):
                        self._service = s
                        self._service_registered = True
                        return self._service

                self._service = PracticalAutostart()
                services.append(self._service)
                self._service_registered = True
                return self._service
        except Exception:
            pass
        return None

    def _get_linux_autostart_file(self) -> Path:
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        return autostart_dir / f"{self.app_name.lower().replace(' ', '_')}.desktop"

    async def enable(self) -> bool:
        """Enable launching the app automatically on system boot."""
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    return await svc.enable()
                except Exception:
                    return False
            return False

        if sys.platform.startswith("linux"):
            try:
                desktop_file = self._get_linux_autostart_file()
                content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name={self.app_name}
Exec={self.app_path}
StartupNotify=false
Terminal=false
X-GNOME-Autostart-enabled=true
"""
                desktop_file.write_text(content, encoding="utf-8")
                return True
            except Exception:
                return False
        return True

    async def disable(self) -> bool:
        """Disable launching the app automatically on system boot."""
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    return await svc.disable()
                except Exception:
                    return False
            return False

        if sys.platform.startswith("linux"):
            try:
                desktop_file = self._get_linux_autostart_file()
                if desktop_file.exists():
                    desktop_file.unlink()
                return True
            except Exception:
                return False
        return True

    async def is_enabled(self) -> bool:
        """Check if auto-start on boot is currently enabled."""
        if self._is_mobile():
            svc = self._ensure_service()
            if svc:
                try:
                    return await svc.is_enabled()
                except Exception:
                    return False
            return False

        if sys.platform.startswith("linux"):
            return self._get_linux_autostart_file().exists()
        return False
