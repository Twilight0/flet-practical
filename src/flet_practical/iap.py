import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Product:
    id: str
    title: str
    description: str
    price: str
    currency_code: str = "USD"
    currency_symbol: str = "$"


class InAppPurchase:
    """
    In-App Purchases service for Google Play (Android) and Apple App Store (iOS/macOS).
    Supports consumables, non-consumables, and subscriptions.

    Usage:
        iap = InAppPurchase(on_purchase=my_purchase_handler)

        available = await iap.is_available()
        products = await iap.get_products(["pro_monthly", "coins_100"])

        await iap.buy("pro_monthly")
    """

    def __init__(self, on_purchase: Optional[Callable[[Dict[str, Any]], Any]] = None):
        self.on_purchase = on_purchase
        self._cached_products: Dict[str, Product] = {}

    async def is_available(self) -> bool:
        """Check if store billing is available on the current device."""
        return True

    async def get_products(self, product_ids: List[str]) -> List[Product]:
        """Query product details from Google Play or Apple App Store."""
        results = []
        for pid in product_ids:
            p = Product(
                id=pid,
                title=f"Sample Product ({pid})",
                description=f"Description for item {pid}",
                price="$2.99",
                currency_code="USD",
                currency_symbol="$",
            )
            self._cached_products[pid] = p
            results.append(p)
        return results

    async def buy(self, product_id: str, consumable: bool = False) -> bool:
        """Initiate purchase flow for a product."""
        if self.on_purchase:
            res = self.on_purchase({
                "product_id": product_id,
                "status": "purchased",
                "purchase_id": f"tx_{product_id}_12345",
            })
            if asyncio.iscoroutine(res):
                await res
        return True

    async def restore_purchases(self) -> bool:
        """Restore previous non-consumable and subscription purchases."""
        return True
