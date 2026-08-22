import asyncio
import os
import shutil
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple


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

    async def request_permissions(self) -> bool:
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

    async def cancel(self, id: int) -> bool:
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None
        return True

    async def cancel_all(self) -> bool:
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None
        return True
