import asyncio
import flet as ft
from flet_practical import BackgroundService


async def main(page: ft.Page):
    page.title = "Practical 8: Background Service Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 760
    page.padding = 24

    bg = BackgroundService(page=page)

    status_label = ft.Text("Service status: checking...", color=ft.Colors.GREY_400)
    battery_label = ft.Text("Battery optimization: unknown", color=ft.Colors.GREY_400)
    counter_label = ft.Text("Background counter: 0", size=18, weight=ft.FontWeight.BOLD)
    log_label = ft.Text("Press Start to keep Python alive after Home", color=ft.Colors.GREY_400, size=12)

    counter = 0
    counter_task: asyncio.Task | None = None

    async def update_status():
        running = await bg.is_running()
        status_label.value = f"Service status: {'RUNNING' if running else 'STOPPED'}"
        status_label.color = ft.Colors.GREEN_400 if running else ft.Colors.GREY_400
        ignoring = await bg.is_ignoring_battery_optimizations()
        battery_label.value = f"Battery optimization: {'IGNORED (good)' if ignoring else 'ACTIVE (may kill background)'}"
        battery_label.color = ft.Colors.GREEN_400 if ignoring else ft.Colors.AMBER_300
        page.update()

    async def counter_loop():
        nonlocal counter
        while True:
            counter += 1
            counter_label.value = f"Background counter: {counter}"
            # Also update page – this will keep incrementing even after Home if service is running
            try:
                page.update()
            except Exception:
                pass
            await asyncio.sleep(1)

    async def on_start(e):
        nonlocal counter_task
        await bg.start(title="Flet Practical Demo", text="Keeping Python alive in background")
        if counter_task is None or counter_task.done():
            counter_task = asyncio.create_task(counter_loop())
        log_label.value = "Service started — press Home, return after 10s, counter should have advanced."
        await update_status()

    async def on_stop(e):
        nonlocal counter_task
        await bg.stop()
        if counter_task:
            counter_task.cancel()
            try:
                await counter_task
            except asyncio.CancelledError:
                pass
        log_label.value = "Service stopped — Python will pause on Home again."
        await update_status()

    async def on_request_battery(e):
        ok = await bg.request_ignore_battery_optimization()
        log_label.value = f"Battery dialog: {'opened' if ok else 'failed/unavailable'}"
        await update_status()

    async def on_open_settings(e):
        await bg.open_ignore_battery_optimization_settings()
        log_label.value = "Opened battery optimization settings."

    # Initial refresh
    await update_status()

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.RUN_CIRCLE, size=28, color=ft.Colors.TEAL_300), ft.Text("Background Service Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Keep the Python isolate alive after returning to Android desktop via a ForegroundService.", color=ft.Colors.GREY_400),
                ft.Divider(),
                status_label,
                battery_label,
                ft.Row([
                    ft.FilledButton("Start Service", icon=ft.Icons.PLAY_ARROW, on_click=on_start),
                    ft.OutlinedButton("Stop Service", icon=ft.Icons.STOP, on_click=on_stop),
                ], wrap=True),
                ft.Row([
                    ft.TextButton("Request Ignore Battery Opt.", on_click=on_request_battery),
                    ft.TextButton("Open Battery Settings", on_click=on_open_settings),
                ], wrap=True),
                ft.Divider(),
                counter_label,
                log_label,
                ft.Text(
                    "Tip: On Xiaomi/Samsung you must disable battery optimization, otherwise Android still kills the service. "
                    "This demo uses flutter_foreground_task — it posts an ongoing notification (required for ForegroundService).",
                    size=11, color=ft.Colors.OUTLINE,
                ),
            ],
            spacing=14,
        )
    )


if __name__ == "__main__":
    ft.run(main)
