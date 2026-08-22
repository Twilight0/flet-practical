import flet as ft
from flet_practical import InAppPurchase


async def main(page: ft.Page):
    page.title = "Practical 6: In-App Purchases Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 650
    page.window.height = 700
    page.padding = 24

    status_label = ft.Text("Ready", color=ft.Colors.GREY_400)

    def on_purchase_event(event_data):
        pid = event_data.get("product_id")
        status = event_data.get("status")
        status_label.value = f"Purchase event: {pid} -> {status}"
        page.update()

    iap = InAppPurchase(on_purchase=on_purchase_event)

    products_list = ft.ListView(expand=1, spacing=10)

    async def load_products():
        products = await iap.get_products(["pro_monthly", "coins_500", "remove_ads"])
        products_list.controls.clear()
        for p in products:
            def make_buy_handler(prod_id):
                async def handler(e):
                    status_label.value = f"Initiating purchase for {prod_id}..."
                    page.update()
                    await iap.buy(prod_id)
                return handler

            products_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(p.title, size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(p.description, size=12, color=ft.Colors.GREY_400),
                                    ],
                                    expand=True,
                                ),
                                ft.Button(
                                    f"Buy {p.price}",
                                    icon=ft.Icons.SHOPPING_BAG,
                                    on_click=make_buy_handler(p.id),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=14,
                    )
                )
            )
        page.update()

    async def on_restore(e):
        await iap.restore_purchases()
        status_label.value = "Restored previous purchases successfully!"
        page.update()

    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.PAYMENTS, size=28, color=ft.Colors.PURPLE_300), ft.Text("In-App Purchases Demo", size=22, weight=ft.FontWeight.BOLD)]),
                ft.Text("Google Play (Android) & Apple App Store (iOS/macOS) in-app billing.", color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Row([
                    ft.Button("Restore Purchases", icon=ft.Icons.RESTORE, on_click=on_restore),
                ]),
                ft.Text("Available Products:", weight=ft.FontWeight.W_500),
                products_list,
                ft.Row([ft.Text("Status: "), status_label]),
            ],
            spacing=14,
            expand=True,
        )
    )

    await load_products()


if __name__ == "__main__":
    ft.run(main)
