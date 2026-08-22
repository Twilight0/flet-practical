import flet as ft
from flet_practical import Clipboard


async def main(page: ft.Page):
    page.title = "Practical 1: Clipboard Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 700
    page.padding = 24

    clipboard = Clipboard()

    input_text = ft.TextField(
        label="Text to Copy",
        value="Hello from Flet Practical Clipboard!",
        multiline=True,
        min_lines=2,
        expand=True,
    )
    pasted_text = ft.TextField(
        label="Pasted Text from Clipboard",
        multiline=True,
        min_lines=2,
        read_only=True,
        expand=True,
    )
    status_label = ft.Text("Ready", color=ft.Colors.GREY_400)

    async def on_copy(e):
        if not input_text.value:
            return
        await clipboard.set_text(input_text.value)
        status_label.value = f"Copied {len(input_text.value)} characters!"
        page.update()

    async def on_paste(e):
        text = await clipboard.get_text()
        pasted_text.value = text or "(Clipboard empty)"
        status_label.value = "Pasted text successfully!"
        page.update()

    async def on_clear(e):
        await clipboard.clear()
        pasted_text.value = ""
        status_label.value = "Clipboard cleared!"
        page.update()

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.CONTENT_PASTE, size=28, color=ft.Colors.PRIMARY), ft.Text("Clipboard Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Cross-platform device clipboard (Text, HTML, Images, Files)", color=ft.Colors.GREY_400),
                ft.Divider(),
                input_text,
                ft.Row([
                    ft.Button("Copy Text", icon=ft.Icons.COPY, on_click=on_copy),
                    ft.OutlinedButton("Paste Text", icon=ft.Icons.PASTE, on_click=on_paste),
                    ft.IconButton(ft.Icons.DELETE_SWEEP, tooltip="Clear", on_click=on_clear),
                ]),
                pasted_text,
                ft.Row([ft.Text("Status: "), status_label]),
            ],
            spacing=14,
        )
    )


if __name__ == "__main__":
    ft.run(main)
