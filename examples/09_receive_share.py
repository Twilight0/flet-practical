import flet as ft
from flet_practical import ReceiveShare


async def main(page: ft.Page):
    page.title = "Practical 9: Receive Share Intent Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 750
    page.padding = 24

    status_label = ft.Text("Waiting for incoming shares...", color=ft.Colors.GREY_400)
    payload_view = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def on_share(files):
        # files is List[Dict] with {path, type, mimeType, thumbnail, duration, message}
        status_label.value = f"Received {len(files)} item(s)"
        status_label.color = ft.Colors.GREEN_400
        payload_view.controls.clear()
        for f in files:
            payload_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f.get("path", ""), weight=ft.FontWeight.BOLD, selectable=True),
                            ft.Text(f"type={f.get('type')} mime={f.get('mimeType')} thumbnail={f.get('thumbnail')}", size=11, color=ft.Colors.GREY_400),
                            ft.Text(f.get("message") or "", size=12) if f.get("message") else ft.Container(),
                        ], spacing=4),
                        padding=12,
                    )
                )
            )
        page.update()

    receive = ReceiveShare(page, on_share=on_share)

    # Also allow manual pull of initial share (if app was launched via share)
    async def on_check_initial(e):
        files = await receive.get_initial_share()
        if files:
            on_share(files)
        else:
            status_label.value = "No initial share found (launch app via System Share Sheet to test)"
            page.update()

    async def on_reset(e):
        await receive.reset()
        status_label.value = "Reset done — share again to test"
        payload_view.controls.clear()
        page.update()

    page.add(
        ft.Column([
            ft.Row([ft.Icon(ft.Icons.INPUT, size=28, color=ft.Colors.TEAL_300), ft.Text("Receive Share Intent Demo", size=22, weight=ft.FontWeight.BOLD)]),
            ft.Text("This app appears in Android's system Share Sheet (text/plain, image/*, video/*). Share a URL/image from Chrome/Gallery to this app to see it here.", color=ft.Colors.GREY_400),
            ft.Divider(),
            status_label,
            ft.Row([ft.FilledButton("Check Initial Share", icon=ft.Icons.DOWNLOAD, on_click=on_check_initial), ft.OutlinedButton("Reset", icon=ft.Icons.CLEAR, on_click=on_reset)], wrap=True),
            ft.Divider(),
            ft.Text("Shared payload:", weight=ft.FontWeight.BOLD),
            ft.Container(content=payload_view, expand=True, border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT), border_radius=8, padding=8),
            ft.Text("Tip: Build APK (flet build apk) and test on device. The share target is registered via receive_sharing_intent and appears in Android's share menu as this app's name.", size=11, color=ft.Colors.OUTLINE),
        ], spacing=14, expand=True)
    )


if __name__ == "__main__":
    ft.run(main)
