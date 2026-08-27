import json
import os
from typing import Any, Callable, List, Optional, Dict

import flet as ft


@ft.control("practical_receive_share")
class PracticalReceiveShare(ft.Service):
    on_share: Optional[ft.EventHandler[ft.ControlEvent]] = None


class ReceiveShare:
    """
    Receive incoming Android/iOS share intents (system share sheet target).

    Replaces the native `ShareReceiverActivity` (ACTION_SEND for text/plain,
    image/*, video/*) with a pure Flet extension. Uses `receive_sharing_intent`
    on the Flutter side.

    Usage:
        receive = ReceiveShare(page, on_share=lambda files: print(files))

        # files is List[Dict] with {path, type, mimeType, thumbnail, duration, message}
        # type is one of: image, video, text, file, url

        # Or pull manually:
        files = await receive.get_initial_share()

    Add once in `main(page)` before `page.add(...)`:
        receive = ReceiveShare(page, on_share=handle_share)
    """

    def __init__(
        self,
        page: Optional[Any] = None,
        on_share: Optional[Callable[[List[Dict[str, Any]]], Any]] = None,
    ):
        self._explicit_page = page
        self.on_share = on_share
        self._service: Optional[PracticalReceiveShare] = None
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

    def _ensure_service(self) -> Optional[PracticalReceiveShare]:
        if self._service_registered and self._service:
            return self._service
        current_page = self.page
        if not current_page:
            return None
        try:
            services = getattr(current_page, "services", None)
            if services is not None:
                for s in services:
                    if isinstance(s, PracticalReceiveShare):
                        self._service = s
                        self._service_registered = True
                        if self.on_share is not None:
                            self._service.on_share = self._on_share_event
                        return self._service
                self._service = PracticalReceiveShare()
                if self.on_share is not None:
                    self._service.on_share = self._on_share_event
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

    async def _on_share_event(self, e: ft.ControlEvent) -> None:
        if self.on_share is None:
            return
        data = e.data
        files: List[Dict[str, Any]] = []
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, list):
                    files = parsed
                elif isinstance(parsed, dict):
                    files = [parsed]
            except Exception:
                files = [{"path": data, "type": "text", "mimeType": "text/plain"}]
        elif isinstance(data, list):
            files = data  # type: ignore
        result = self.on_share(files)
        if hasattr(result, "__await__"):
            await result  # type: ignore

    async def get_initial_share(self) -> List[Dict[str, Any]]:
        svc = self._ensure_service()
        if svc:
            try:
                res = await svc._invoke_method("get_initial_share")
                if isinstance(res, list):
                    return res  # type: ignore
                if isinstance(res, str):
                    try:
                        parsed = json.loads(res)
                        if isinstance(parsed, list):
                            return parsed
                    except Exception:
                        pass
            except Exception:
                pass
        return []

    async def reset(self) -> bool:
        svc = self._ensure_service()
        if svc:
            try:
                await svc._invoke_method("reset")
                return True
            except Exception:
                pass
        return False
