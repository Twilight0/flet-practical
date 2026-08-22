import subprocess
import sys
import flet as ft


async def main(page: ft.Page):
    page.title = "Flet Practical Extension Suite Hub"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 750
    page.window.height = 850
    page.padding = 24

    features = [
        ("1. Device Clipboard", "Read/Write text, HTML, raw images, and file paths", ft.Icons.CONTENT_PASTE, ft.Colors.BLUE_400, "01_clipboard.py"),
        ("2. Local Notifications", "Trigger local & persistent (ongoing status bar) notifications", ft.Icons.NOTIFICATIONS, ft.Colors.AMBER_400, "02_notifications.py"),
        ("3. Screen WakeLock", "Keep screen awake and prevent display sleep during tasks", ft.Icons.LOCK_CLOCK, ft.Colors.CYAN_400, "03_wakelock.py"),
        ("4. Edge Neural TTS", "Microsoft Edge high-quality neural speech synthesis", ft.Icons.RECORD_VOICE_OVER, ft.Colors.GREEN_400, "04_tts.py"),
        ("5. Auto-Start on Boot", "Configure automatic startup on system boot / device launch", ft.Icons.RESTART_ALT, ft.Colors.ORANGE_400, "05_autostart.py"),
        ("6. In-App Purchases", "Google Play & Apple App Store in-app billing & products", ft.Icons.PAYMENTS, ft.Colors.PURPLE_300, "06_iap.py"),
        ("7. Native Share Intent", "Open native OS Share Sheet (ACTION_SEND / UIActivityViewController)", ft.Icons.SHARE, ft.Colors.TEAL_300, "07_share.py"),
    ]

    cards = []
    for title, desc, icon, color, filename in features:
        def make_launch_handler(script_name):
            def handler(e):
                subprocess.Popen([sys.executable, f"examples/{script_name}"])
            return handler

        cards.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(icon, size=36, color=color),
                            ft.Column(
                                [
                                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(desc, size=12, color=ft.Colors.GREY_400),
                                ],
                                expand=True,
                            ),
                            ft.Button("Launch Demo", icon=ft.Icons.PLAY_ARROW, on_click=make_launch_handler(filename)),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=16,
                )
            )
        )

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.EXTENSION, size=32, color=ft.Colors.PRIMARY), ft.Text("Flet Practical Extension Suite", size=24, weight=ft.FontWeight.BOLD)]),
                ft.Text("Bundled essential device utilities for Android, iOS, Desktop, and Web.", color=ft.Colors.GREY_400),
                ft.Divider(height=16),
                ft.Column(cards, spacing=12),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.run(main)
