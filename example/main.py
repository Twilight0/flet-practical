import flet as ft
from flet_clipboard import Clipboard


async def main(page: ft.Page):
    page.title = "Flet Clipboard Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 750
    page.window.height = 800
    page.padding = 24

    clipboard = Clipboard()
    page.overlay.append(clipboard)

    # UI Elements
    status_text = ft.Text("Ready", size=13, color=ft.Colors.GREY_400)

    # Text section
    input_text = ft.TextField(
        label="Text to Copy",
        hint_text="Enter text here and click Copy...",
        multiline=True,
        min_lines=2,
        max_lines=4,
        expand=True,
    )
    pasted_text_display = ft.TextField(
        label="Clipboard Text Content",
        multiline=True,
        min_lines=2,
        max_lines=4,
        read_only=True,
        expand=True,
    )

    # HTML section
    pasted_html_display = ft.TextField(
        label="Clipboard HTML Content",
        multiline=True,
        min_lines=2,
        max_lines=3,
        read_only=True,
        expand=True,
    )

    # Image section
    image_preview = ft.Image(
        src_base64="",
        width=300,
        height=200,
        fit=ft.ImageFit.CONTAIN,
        visible=False,
    )
    no_image_text = ft.Text("No image on clipboard", italic=True, color=ft.Colors.GREY_500)

    # Files section
    files_list = ft.ListView(expand=1, spacing=4, height=100)

    def show_snack(msg: str, is_error: bool = False):
        page.overlay.append(
            ft.SnackBar(
                content=ft.Text(msg),
                bgcolor=ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700,
                open=True,
            )
        )
        page.update()

    async def on_copy_text(e):
        text = input_text.value or ""
        if not text:
            show_snack("Please enter some text to copy!", is_error=True)
            return
        success = await clipboard.set_text(text)
        if success:
            show_snack("Copied text to clipboard!")
            status_text.value = f"Copied {len(text)} characters"
        page.update()

    async def on_paste_text(e):
        text = await clipboard.get_text()
        if text:
            pasted_text_display.value = text
            status_text.value = f"Pasted {len(text)} characters"
            show_snack("Pasted text from clipboard!")
        else:
            pasted_text_display.value = "(Clipboard has no text)"
            status_text.value = "No text on clipboard"
            show_snack("Clipboard is empty or contains no text", is_error=True)
        page.update()

    async def on_paste_html(e):
        html = await clipboard.get_html()
        if html:
            pasted_html_display.value = html
            status_text.value = f"Pasted HTML ({len(html)} chars)"
            show_snack("Pasted HTML from clipboard!")
        else:
            pasted_html_display.value = "(No HTML content found)"
            status_text.value = "No HTML on clipboard"
            show_snack("No HTML content on clipboard", is_error=True)
        page.update()

    async def on_paste_image(e):
        b64 = await clipboard.get_image_base64()
        if b64:
            image_preview.src_base64 = b64
            image_preview.visible = True
            no_image_text.visible = False
            status_text.value = f"Image loaded from clipboard ({len(b64)} b64 bytes)"
            show_snack("Image loaded from clipboard!")
        else:
            image_preview.visible = False
            no_image_text.visible = True
            status_text.value = "No image on clipboard"
            show_snack("No image found on clipboard", is_error=True)
        page.update()

    async def on_paste_files(e):
        files = await clipboard.get_files()
        files_list.controls.clear()
        if files:
            for f in files:
                files_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.INSERT_DRIVE_FILE),
                        title=ft.Text(f, size=13),
                    )
                )
            status_text.value = f"Found {len(files)} files on clipboard"
            show_snack(f"Found {len(files)} files on clipboard!")
        else:
            files_list.controls.append(ft.Text("No file paths copied on clipboard", italic=True))
            status_text.value = "No files on clipboard"
            show_snack("No file paths on clipboard", is_error=True)
        page.update()

    async def on_clear_clipboard(e):
        await clipboard.clear()
        pasted_text_display.value = ""
        pasted_html_display.value = ""
        image_preview.visible = False
        no_image_text.visible = True
        files_list.controls.clear()
        status_text.value = "Clipboard cleared"
        show_snack("Clipboard cleared!")
        page.update()

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CONTENT_PASTE, size=32, color=ft.Colors.PRIMARY),
                        ft.Text("Flet Clipboard Extension", size=24, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text("Cross-platform device clipboard access powered by Pasteboard.", color=ft.Colors.GREY_400),
                ft.Divider(height=16),
                # Section 1: Text
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Text Clipboard", size=16, weight=ft.FontWeight.BOLD),
                                ft.Row([input_text]),
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Copy to Clipboard", icon=ft.Icons.COPY, on_click=on_copy_text),
                                        ft.OutlinedButton("Paste Text", icon=ft.Icons.PASTE, on_click=on_paste_text),
                                    ]
                                ),
                                ft.Row([pasted_text_display]),
                            ],
                            spacing=10,
                        ),
                        padding=16,
                    )
                ),
                # Section 2: Image & Rich Content
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Rich Content & Images", size=16, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Paste Image", icon=ft.Icons.IMAGE, on_click=on_paste_image),
                                        ft.OutlinedButton("Paste HTML", icon=ft.Icons.CODE, on_click=on_paste_html),
                                        ft.OutlinedButton("Paste Files", icon=ft.Icons.FOLDER, on_click=on_paste_files),
                                        ft.IconButton(ft.Icons.DELETE_SWEEP, tooltip="Clear Clipboard", on_click=on_clear_clipboard),
                                    ]
                                ),
                                image_preview,
                                no_image_text,
                                pasted_html_display,
                                ft.Text("Copied Files:", weight=ft.FontWeight.W_500),
                                files_list,
                            ],
                            spacing=10,
                        ),
                        padding=16,
                    )
                ),
                ft.Row([ft.Text("Status: "), status_text]),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
