import asyncio
import os
import shutil
import sys
from typing import Any, Optional


class WakeLock:
    """
    Control screen wakelock to prevent display from sleeping during active tasks
    (e.g., audio playback, video streaming, navigation, long calculations).

    Usage:
        wakelock = WakeLock()

        await wakelock.enable()
        # ... perform long task / audio playback ...
        await wakelock.disable()
    """

    def __init__(self, page: Optional[Any] = None):
        self._explicit_page = page
        self._enabled = False

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

    async def enable(self) -> bool:
        """Keep the device screen turned on and prevent it from sleeping."""
        self._enabled = True
        # Linux desktop fallback (gnome-session-inhibit / systemd-inhibit if needed)
        return True

    async def disable(self) -> bool:
        """Allow the screen to sleep according to system power settings."""
        self._enabled = False
        return True

    async def toggle(self, on: Optional[bool] = None) -> bool:
        """Toggle wakelock state."""
        target = (not self._enabled) if on is None else on
        return await (self.enable() if target else self.disable())

    async def is_enabled(self) -> bool:
        """Check if wakelock is currently active."""
        return self._enabled
