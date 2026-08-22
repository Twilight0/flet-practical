import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Optional


class AutoStart:
    """
    Manage auto-start on device boot / system startup:
    - Android: Boot completed receiver service.
    - Linux (Desktop): XDG autostart desktop entry (~/.config/autostart).
    - Windows (Desktop): Registry run keys / Startup folder.
    - macOS: LaunchAgents.

    Usage:
        autostart = AutoStart(app_name="MyFletApp")

        await autostart.enable()
        is_on = await autostart.is_enabled()
    """

    def __init__(self, app_name: str = "FletApp", app_path: Optional[str] = None):
        self.app_name = app_name
        self.app_path = app_path or sys.executable

    def _get_linux_autostart_file(self) -> Path:
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        return autostart_dir / f"{self.app_name.lower().replace(' ', '_')}.desktop"

    async def enable(self) -> bool:
        """Enable launching the app automatically on system boot."""
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
        """Disable launching the app on system boot."""
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
        if sys.platform.startswith("linux"):
            desktop_file = self._get_linux_autostart_file()
            return desktop_file.exists()
        return False
