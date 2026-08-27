import flet as ft
from flet_practical import AutoStart


async def main(page: ft.Page):
    page.title = "Practical 5: Auto-Start on Boot Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 700
    page.padding = 24

    autostart = AutoStart(app_name="FletPracticalDemo", page=page)

    is_active = await autostart.is_enabled()
    status_label = ft.Text(
        f"Auto-start status: {'ENABLED' if is_active else 'DISABLED'}",
        size=16,
        weight=ft.FontWeight.W_500,
        color=ft.Colors.GREEN_400 if is_active else ft.Colors.GREY_400,
    )
    toggle_btn = ft.Button(
        "Disable Auto-Start" if is_active else "Enable Auto-Start",
        icon=ft.Icons.POWER_SETTINGS_NEW,
    )

    async def on_toggle(e):
        current = await autostart.is_enabled()
        if current:
            await autostart.disable()
            status_label.value = "Auto-start status: DISABLED"
            status_label.color = ft.Colors.GREY_400
            toggle_btn.text = "Enable Auto-Start"
        else:
            await autostart.enable()
            status_label.value = "Auto-start status: ENABLED"
            status_label.color = ft.Colors.GREEN_400
            toggle_btn.text = "Disable Auto-Start"
        page.update()

    toggle_btn.on_click = on_toggle

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.RESTART_ALT, size=28, color=ft.Colors.ORANGE_400), ft.Text("Auto-Start on Boot Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Configure the application to automatically launch on system startup / device boot.", color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(
                        [
                            status_label,
                            toggle_btn,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16,
                    ),
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            spacing=14,
        )
    )


if __name__ == "__main__":
    ft.run(main)
