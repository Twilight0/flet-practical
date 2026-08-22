import flet as ft
from flet_practical import WakeLock


async def main(page: ft.Page):
    page.title = "Practical 3: Screen WakeLock Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 700
    page.padding = 24

    wakelock = WakeLock()

    icon = ft.Icon(ft.Icons.LOCK_CLOCK, size=64, color=ft.Colors.GREY_500)
    status_label = ft.Text("WakeLock is INACTIVE (Screen will sleep normally)", size=16, weight=ft.FontWeight.W_500)
    toggle_btn = ft.Button("Enable WakeLock", icon=ft.Icons.LIGHTBULB)

    async def on_toggle(e):
        is_on = await wakelock.is_enabled()
        if is_on:
            await wakelock.disable()
            icon.name = ft.Icons.LOCK_CLOCK
            icon.color = ft.Colors.GREY_500
            status_label.value = "WakeLock is INACTIVE (Screen will sleep normally)"
            toggle_btn.text = "Enable WakeLock"
            toggle_btn.icon = ft.Icons.LIGHTBULB
        else:
            await wakelock.enable()
            icon.name = ft.Icons.LIGHTBULB_CIRCLE
            icon.color = ft.Colors.AMBER_400
            status_label.value = "WakeLock is ACTIVE (Screen will stay ON indefinitely)"
            toggle_btn.text = "Disable WakeLock"
            toggle_btn.icon = ft.Icons.LIGHTBULB_OUTLINE
        page.update()

    toggle_btn.on_click = on_toggle

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.SCREEN_LOCK_PORTRAIT, size=28, color=ft.Colors.CYAN_400), ft.Text("Screen WakeLock Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Prevent display from sleeping during audio playback, video, or long tasks.", color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(
                        [
                            icon,
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
