import asyncio
import os
import shutil
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple
import flet as ft


@ft.control("practical_notifications")
class PracticalNotifications(ft.Service):
    on_click: Optional[ft.EventHandler[ft.ControlEvent]] = None

    async def request_permissions(self) -> bool:
        return await self._invoke_method("request_permissions")

    async def are_notifications_enabled(self) -> bool:
        return await self._invoke_method("are_notifications_enabled")

    async def show(
        self,
        title: str,
        body: str,
        id: int = 1,
        payload: Optional[str] = None,
        channel_id: str = "flet_practical_default",
        channel_name: str = "Default Channel",
        channel_description: str = "",
        ongoing: bool = False,
        auto_cancel: Optional[bool] = None,
        play_sound: bool = True,
        enable_vibration: bool = True,
    ) -> bool:
        if auto_cancel is None:
            auto_cancel = not ongoing
        return await self._invoke_method(
            "show",
            arguments={
                "id": id,
                "title": title,
                "body": body,
                "payload": payload,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_description": channel_description,
                "ongoing": ongoing,
                "auto_cancel": auto_cancel,
                "play_sound": play_sound,
                "enable_vibration": enable_vibration,
            },
        )

    async def cancel(self, id: int = 1) -> bool:
        return await self._invoke_method("cancel", arguments={"id": id})

    async def cancel_all(self) -> bool:
        return await self._invoke_method("cancel_all")


class Notifications:
    """
    Local and persistent notification service:
    - Android: Notification channels, persistent status bar alerts, action clicks.
    - iOS & macOS: System banners, badges, alerts.
    - Linux (Desktop): FreeDesktop notifications / notify-send with interactive actions.
    - Windows: WinToast / Action Center alerts.
    """

    def __init__(self, page: Optional[Any] = None, on_click: Optional[Callable[[str], Any]] = None):
        self._explicit_page = page
        self.on_click = on_click
        self._current_task: Optional[asyncio.Task] = None
        self._service: Optional[PracticalNotifications] = None
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

    async def _ensure_service(self) -> Optional[PracticalNotifications]:
        if self._service_registered and self._service:
            return self._service

        current_page = self.page
        if not current_page:
            return None

        try:
            services = getattr(current_page, "services", None)
            if services is not None:
                for s in services:
                    if isinstance(s, PracticalNotifications):
                        self._service = s
                        self._service_registered = True
                        return self._service

                self._service = PracticalNotifications()
                if self.on_click is not None:
                    self._service.on_click = self._on_click_event
                # Flet diffs services by list identity - in-place append never mounts.
                try:
                    current_page.services = [*services, self._service]
                except Exception:
                    services.append(self._service)
                self._service_registered = True
                if hasattr(current_page, "update"):
                    try:
                        maybe = current_page.update()
                        if asyncio.iscoroutine(maybe):
                            await maybe
                        await asyncio.sleep(1.5)
                        try:
                            maybe2 = current_page.update()
                            if asyncio.iscoroutine(maybe2):
                                await maybe2
                        except Exception:
                            pass
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass
                return self._service
        except Exception:
            pass
        return None

    async def request_permissions(self) -> bool:
        svc = await self._ensure_service()
        if svc and self.page and getattr(self.page, "platform", None) in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, "android", "ios"):
            try:
                return await svc.request_permissions()
            except Exception:
                pass
        return True

    async def _on_click_event(self, e: ft.ControlEvent) -> None:
        """Adapter: mobile tap event (ControlEvent.data = payload) -> user on_click(str)."""
        if self.on_click is None:
            return
        payload = getattr(e, "data", "") or ""
        result = self.on_click(payload)
        if asyncio.iscoroutine(result):
            await result

    async def are_notifications_enabled(self) -> bool:
        svc = await self._ensure_service()
        if svc and self.page and getattr(self.page, "platform", None) in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, "android", "ios"):
            try:
                return await svc.are_notifications_enabled()
            except Exception:
                pass
        return True

    async def show(
        self,
        title: str,
        body: str,
        id: int = 1,
        payload: Optional[str] = None,
        channel_id: str = "flet_practical_notifications",
        channel_name: str = "General Notifications",
        channel_description: str = "",
        ongoing: bool = False,
        auto_cancel: Optional[bool] = None,
        play_sound: bool = True,
        enable_vibration: bool = True,
        actions: Optional[List[Tuple[str, str]]] = None,
        on_action: Optional[Callable[[str], Any]] = None,
    ) -> bool:
        """
        Display a notification.
        Set ongoing=True to make the notification persistent.
        Pass actions=[("key", "Button Label"), ...] for interactive buttons.
        """
        if auto_cancel is None:
            auto_cancel = not ongoing

        svc = await self._ensure_service()
        if svc and self.page and getattr(self.page, "platform", None) in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, "android", "ios"):
            show_args = dict(
                title=title,
                body=body,
                id=id,
                payload=payload,
                channel_id=channel_id,
                channel_name=channel_name,
                channel_description=channel_description,
                ongoing=ongoing,
                auto_cancel=auto_cancel,
                play_sound=play_sound,
                enable_vibration=enable_vibration,
            )
            try:
                return await svc.show(**show_args)
            except Exception as ex:
                if "Timeout" not in str(type(ex)) and "Timeout" not in str(ex):
                    print(f"Error calling mobile notification service: {ex}")
                    return False
                # Listener gone (control never mounted or disposed on rebuild):
                # drop the dead handle, remount fresh, retry once.
                self._service = None
                self._service_registered = False
                try:
                    svc = await self._ensure_service()
                    if svc:
                        return await svc.show(**show_args)
                except Exception as ex2:
                    print(f"Error calling mobile notification service: {ex2}")
                return False

        # Linux Desktop with interactive actions
        if sys.platform.startswith("linux") and shutil.which("notify-send"):
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()

            async def _run_desktop_notification():
                try:
                    urgency = "critical" if ongoing else "normal"
                    cmd = ["notify-send", "-u", urgency, "-a", channel_name]

                    if actions:
                        for act_key, act_label in actions:
                            cmd.extend(["-A", f"{act_key}={act_label}"])

                    cmd.extend([title, body])

                    proc = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    stdout, _ = await proc.communicate()
                    chosen_action = (stdout.decode("utf-8") if stdout else "").strip()

                    cb = on_action or self.on_click
                    if chosen_action and cb:
                        res = cb(chosen_action)
                        if asyncio.iscoroutine(res):
                            await res
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

            self._current_task = asyncio.create_task(_run_desktop_notification())
            return True

        return True

    async def cancel(self, id: int = 1) -> bool:
        svc = await self._ensure_service()
        if svc and self.page and getattr(self.page, "platform", None) in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, "android", "ios"):
            try:
                return await svc.cancel(id)
            except Exception:
                pass

        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None
        return True

    async def cancel_all(self) -> bool:
        svc = await self._ensure_service()
        if svc and self.page and getattr(self.page, "platform", None) in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, "android", "ios"):
            try:
                return await svc.cancel_all()
            except Exception:
                pass

        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None
        return True
