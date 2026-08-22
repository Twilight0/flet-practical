import flet as ft
from flet_practical import Notifications


async def main(page: ft.Page):
    page.title = "Practical 2: Local Notifications Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 700
    page.padding = 24

    notifications = Notifications()

    title_input = ft.TextField(label="Notification Title", value="Download Completed")
    body_input = ft.TextField(label="Notification Body", value="Your report 'export_2026.pdf' has finished.", multiline=True)
    persistent_switch = ft.Switch(label="Persistent (Ongoing on Android / cannot be swiped away)", value=False)
    status_label = ft.Text("Ready", color=ft.Colors.GREY_400)

    async def on_send(e):
        title = title_input.value or "Alert"
        body = body_input.value or "Notification test"
        ongoing = persistent_switch.value

        success = await notifications.show(
            id=101,
            title=title,
            body=body,
            ongoing=ongoing,
        )
        if success:
            status_label.value = f"Sent {'persistent' if ongoing else 'standard'} notification!"
        else:
            status_label.value = "Notification triggered (desktop/system fallback)."
        page.update()

    async def on_cancel(e):
        await notifications.cancel(101)
        status_label.value = "Canceled notification #101"
        page.update()

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.NOTIFICATIONS, size=28, color=ft.Colors.AMBER_400), ft.Text("Local Notifications Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Cross-platform local notifications with persistent / ongoing status bar support.", color=ft.Colors.GREY_400),
                ft.Divider(),
                title_input,
                body_input,
                persistent_switch,
                ft.Row([
                    ft.Button("Send Notification", icon=ft.Icons.SEND, on_click=on_send),
                    ft.OutlinedButton("Cancel Notification", icon=ft.Icons.CANCEL, on_click=on_cancel),
                ]),
                ft.Row([ft.Text("Status: "), status_label]),
            ],
            spacing=14,
        )
    )


if __name__ == "__main__":
    ft.run(main)
