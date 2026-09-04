import asyncio
import io
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Dict, List, Optional


# NOTE: edge_tts is imported lazily inside get_voices()/speak() so that
# `import flet_practical` doesn't pay ~1s + tens of MB for an unused TTS engine.


class TtsService:
    """
    Microsoft Edge Neural Speech Synthesis service.
    High quality neural voices with rate, pitch, volume, and voice customization.

    Usage:
        tts = TtsService(voice="en-US-JennyNeural")
        await tts.speak("Hello from Flet Practical!")
    """

    def __init__(
        self,
        voice: str = "en-US-JennyNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        on_start: Optional[Callable[[], Any]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], Any]] = None,
        on_error: Optional[Callable[[str], Any]] = None,
    ):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.on_start = on_start
        self.on_complete = on_complete
        self.on_error = on_error

        self._current_audio_data: Optional[bytes] = None
        self._playback_process: Optional[subprocess.Popen] = None

    @classmethod
    def preload(cls) -> bool:
        """Eagerly load the edge_tts engine now (opt-in).

        Import is lazy by default so non-TTS apps start fast. Call this once
        during splash/loading if you know TTS will be needed, so the first
        speak()/get_voices() has no import hiccup:
            TtsService.preload()
        Returns True if the engine is available.
        """
        try:
            import edge_tts  # noqa: F401
            return True
        except Exception:
            return False

    async def get_voices(self) -> List[Dict[str, Any]]:
        """Retrieve list of all available Microsoft neural voices."""
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            return [
                {
                    "ShortName": v.get("ShortName", ""),
                    "FriendlyName": v.get("FriendlyName", ""),
                    "Locale": v.get("Locale", ""),
                    "Gender": v.get("Gender", ""),
                }
                for v in voices
            ]
        except Exception as ex:
            if self.on_error:
                self.on_error(str(ex))
            return []

    async def speak(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        volume: Optional[str] = None,
        play_immediately: bool = True,
    ) -> Optional[bytes]:
        """Synthesize speech and optionally play it immediately through system speakers."""
        if not text or not text.strip():
            return None

        v = voice or self.voice
        r = rate or self.rate
        p = pitch or self.pitch
        vol = volume or self.volume

        if self.on_start:
            res = self.on_start()
            if asyncio.iscoroutine(res):
                await res

        try:
            import edge_tts  # lazy: don't burden non-TTS apps at import time
            communicate = edge_tts.Communicate(text=text, voice=v, rate=r, pitch=p, volume=vol)
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])

            audio_data = audio_buffer.getvalue()
            self._current_audio_data = audio_data

            if play_immediately and audio_data:
                await self._play_audio(audio_data)

            if self.on_complete:
                res = self.on_complete({"bytes": len(audio_data)})
                if asyncio.iscoroutine(res):
                    await res

            return audio_data
        except Exception as ex:
            if self.on_error:
                res = self.on_error(str(ex))
                if asyncio.iscoroutine(res):
                    await res
            raise ex

    async def _play_audio(self, audio_data: bytes) -> None:
        """Play audio bytes via available system media player."""
        player = None
        for cmd in ["mpv", "ffplay", "aplay", "paplay"]:
            if shutil.which(cmd):
                player = cmd
                break

        if not player:
            return

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                tmp_path = f.name

            args = [player]
            if player == "mpv":
                args.extend(["--no-video", "--really-quiet", tmp_path])
            elif player == "ffplay":
                args.extend(["-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path])
            else:
                args.append(tmp_path)

            self._playback_process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    async def stop(self) -> None:
        """Stop active speech audio playback."""
        if self._playback_process:
            try:
                self._playback_process.terminate()
                self._playback_process = None
            except Exception:
                pass

    async def get_audio_data(self) -> Optional[bytes]:
        """Get the latest synthesized audio MP3 bytes."""
        return self._current_audio_data
