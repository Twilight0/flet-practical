import os
from typing import Any, Optional

import flet as ft


@ft.control("practical_background_service")
class PracticalBackgroundService(ft.Service):
    async def start(self, title: str = "Running in background", text: str = "Tap to return to app", channel_id: str = "flet_practical_background", channel_name: str = "Background Service"):
        return await self._invoke_method("start", arguments={"title": title, "text": text, "channel_id": channel_id, "channel_name": channel_name})

    async def stop(self):
        return await self._invoke_method("stop")

    async def is_running(self):
        return await self._invoke_method("is_running")

    async def restart(self):
        return await self._invoke_method("restart")

    async def is_ignoring_battery_optimizations(self):
        return await self._invoke_method("is_ignoring_battery_optimizations")

    async def request_ignore_battery_optimization(self):
        return await self._invoke_method("request_ignore_battery_optimization")

    async def open_ignore_battery_optimization_settings(self):
        return await self._invoke_method("open_ignore_battery_optimization_settings")


class BackgroundService:
    """
    Keep the app's Python isolate alive when the user returns to the Android desktop.

    Wraps `flutter_foreground_task` as a `ForegroundService` with an ongoing notification.
    Without this the `Activity` goes `STOPPED` and Android kills the FlutterEngine + Python bridge in seconds.

    Usage:
        bg = BackgroundService(page)
        await bg.request_ignore_battery_optimization() # optional, for Xiaomi/Samsung
        await bg.start(title="InstaSave", text="Upscaling in background...")
        # ... your long Python thread / asyncio work ...
        await bg.stop()

    Works on Android only; on iOS/Linux/Web/Desktop the calls are no-ops and return True/False.
    """

    def __init__(self, page: Optional[Any] = None):
        self._explicit_page = page
        self._service: Optional[PracticalBackgroundService] = None
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
        current_page = self.page
        if current_page and hasattr(current_page, "platform"):
            try:
                p = current_page.platform
                s = str(p).lower()
                if "android" in s:
                    return True
                if hasattr(p, "is_mobile") and callable(getattr(p, "is_mobile")):
                    try:
                        if p.is_mobile():
                            return True
                    except Exception:
                        pass
            except Exception:
                pass
        return "ANDROID_ARGUMENT" in os.environ or "ANDROID_ROOT" in os.environ

    def _ensure_service(self) -> Optional[PracticalBackgroundService]:
        if self._service_registered and self._service:
            return self._service
        current_page = self.page
        if not current_page:
            return None
        try:
            services = getattr(current_page, "services", None)
            if services is not None:
                for s in services:
                    if isinstance(s, PracticalBackgroundService):
                        self._service = s
                        self._service_registered = True
                        return self._service
                self._service = PracticalBackgroundService()
                services.append(self._service)
                self._service_registered = True
                if hasattr(current_page, "update"):
                    try:
                        current_page.update()
                    except Exception:
                        pass
                return self._service
        except Exception:
            pass
        return None

    async def start(self, title: str = "Running in background", text: str = "Tap to return to app", channel_id: str = "flet_practical_background", channel_name: str = "Background Service") -> bool:
        if not self._is_mobile():
            return True
        svc = self._ensure_service()
        if svc:
            try:
                res = await svc.start(title=title, text=text, channel_id=channel_id, channel_name=channel_name)
                return bool(res)
            except Exception:
                pass
        return False

    async def stop(self) -> bool:
        if not self._is_mobile():
            return True
        svc = self._ensure_service()
        if svc:
            try:
                res = await svc.stop()
                return bool(res)
            except Exception:
                pass
        return False

    async def is_running(self) -> bool:
        if not self._is_mobile():
            return False
        svc = self._ensure_service()
        if svc:
            try:
                return bool(await svc.is_running())
            except Exception:
                pass
        return False

    async def restart(self) -> bool:
        if not self._is_mobile():
            return False
        svc = self._ensure_service()
        if svc:
            try:
                return bool(await svc.restart())
            except Exception:
                pass
        return False

    async def is_ignoring_battery_optimizations(self) -> bool:
        svc = self._ensure_service()
        if svc:
            try:
                return bool(await svc.is_ignoring_battery_optimizations())
            except Exception:
                pass
        return True

    async def request_ignore_battery_optimization(self) -> bool:
        svc = self._ensure_service()
        if svc:
            try:
                return bool(await svc.request_ignore_battery_optimization())
            except Exception:
                pass
        return True

    async def open_ignore_battery_optimization_settings(self) -> bool:
        svc = self._ensure_service()
        if svc:
            try:
                return bool(await svc.open_ignore_battery_optimization_settings())
            except Exception:
                pass
        return False
