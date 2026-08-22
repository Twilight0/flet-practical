import flet as ft
from flet_practical import Share


async def main(page: ft.Page):
    page.title = "Practical 7: Native Share Intent Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 700
    page.padding = 24

    share = Share()

    text_input = ft.TextField(
        label="Text / Link to Share",
        value="Check out this awesome Flet Practical extension: https://github.com/Twilight0/flet-practical",
        multiline=True,
        min_lines=2,
    )
    subject_input = ft.TextField(label="Subject / Title (Optional)", value="Interesting Project")
    status_label = ft.Text("Ready", color=ft.Colors.GREY_400)

    async def on_share_text(e):
        text = text_input.value or ""
        subject = subject_input.value or None
        if not text:
            return
        status_label.value = "Opening system Share Sheet..."
        page.update()

        success = await share.share_text(text, subject=subject)
        status_label.value = "Share intent opened successfully!" if success else "Failed to open share sheet"
        page.update()

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.SHARE, size=28, color=ft.Colors.TEAL_300), ft.Text("Native Share Intent Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Trigger the native system Share Sheet on Android (ACTION_SEND), iOS (UIActivityViewController), Desktop, and Web.", color=ft.Colors.GREY_400),
                ft.Divider(),
                text_input,
                subject_input,
                ft.Row([
                    ft.Button("Open Share Sheet", icon=ft.Icons.SHARE, on_click=on_share_text),
                ]),
                ft.Row([ft.Text("Status: "), status_label]),
            ],
            spacing=14,
        )
    )


if __name__ == "__main__":
    ft.run(main)
