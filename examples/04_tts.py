import flet as ft
from flet_practical import TtsService


async def main(page: ft.Page):
    page.title = "Practical 4: Microsoft Neural TTS Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 700
    page.window.height = 750
    page.padding = 24

    tts = TtsService(voice="en-US-JennyNeural")

    text_input = ft.TextField(
        label="Text to Speak",
        value="Welcome to Flet Practical! This is high quality Microsoft Edge Neural Speech Synthesis running in Python.",
        multiline=True,
        min_lines=3,
        expand=True,
    )
    voice_dropdown = ft.Dropdown(
        label="Neural Voice",
        options=[
            ft.dropdown.Option("en-US-JennyNeural", "Jenny (US English, Female)"),
            ft.dropdown.Option("en-US-GuyNeural", "Guy (US English, Male)"),
            ft.dropdown.Option("en-GB-SoniaNeural", "Sonia (UK English, Female)"),
            ft.dropdown.Option("en-AU-NatashaNeural", "Natasha (AU English, Female)"),
            ft.dropdown.Option("el-GR-AthinaNeural", "Athina (Greek, Female)"),
            ft.dropdown.Option("fr-FR-DeniseNeural", "Denise (French, Female)"),
            ft.dropdown.Option("de-DE-KatjaNeural", "Katja (German, Female)"),
            ft.dropdown.Option("es-ES-ElviraNeural", "Elvira (Spanish, Female)"),
        ],
        value="en-US-JennyNeural",
        expand=True,
    )
    status_label = ft.Text("Ready", color=ft.Colors.GREY_400)
    speak_btn = ft.Button("Speak Text", icon=ft.Icons.VOLUME_UP)
    stop_btn = ft.OutlinedButton("Stop", icon=ft.Icons.STOP, disabled=True)

    async def on_speak(e):
        text = (text_input.value or "").strip()
        if not text:
            return
        tts.voice = voice_dropdown.value or "en-US-JennyNeural"
        speak_btn.disabled = True
        stop_btn.disabled = False
        status_label.value = f"Speaking ({tts.voice})..."
        page.update()

        try:
            audio_data = await tts.speak(text, play_immediately=True)
            if audio_data:
                status_label.value = f"Finished ({len(audio_data):,} bytes synthesized)"
        except Exception as ex:
            status_label.value = f"Error: {ex}"
        finally:
            speak_btn.disabled = False
            stop_btn.disabled = True
            page.update()

    async def on_stop(e):
        await tts.stop()
        status_label.value = "Stopped"
        stop_btn.disabled = True
        speak_btn.disabled = False
        page.update()

    speak_btn.on_click = on_speak
    stop_btn.on_click = on_stop

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.RECORD_VOICE_OVER, size=28, color=ft.Colors.GREEN_400), ft.Text("Neural Text to Speech Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Synthesize neural speech using Microsoft's Edge TTS engine.", color=ft.Colors.GREY_400),
                ft.Divider(),
                text_input,
                ft.Row([voice_dropdown]),
                ft.Row([speak_btn, stop_btn]),
                ft.Row([ft.Text("Status: "), status_label]),
            ],
            spacing=14,
        )
    )


if __name__ == "__main__":
    ft.run(main)
