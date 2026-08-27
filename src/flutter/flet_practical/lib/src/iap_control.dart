import 'dart:async';
import 'dart:convert';
import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:in_app_purchase/in_app_purchase.dart';

class PracticalIapControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalIapControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalIapControl> createState() => _PracticalIapControlState();
}

class _PracticalIapControlState extends State<PracticalIapControl> {
  final InAppPurchase _iap = InAppPurchase.instance;
  StreamSubscription<List<PurchaseDetails>>? _subscription;
  final Map<String, ProductDetails> _cachedProducts = {};

  @override
  void initState() {
    super.initState();
    _initIapStream();
    _registerMethodHandlers();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  void _initIapStream() {
    _subscription = _iap.purchaseStream.listen((List<PurchaseDetails> purchases) {
      for (final purchase in purchases) {
        final Map<String, dynamic> data = {
          "product_id": purchase.productID,
          "purchase_id": purchase.purchaseID,
          "status": purchase.status.name, // pending, purchased, error, restored, canceled
          "transaction_date": purchase.transactionDate,
          "error": purchase.error?.message,
        };
        widget.control.triggerEvent("purchase_updated", jsonEncode(data));

        if (purchase.pendingCompletePurchase) {
          _iap.completePurchase(purchase);
        }
      }
    });
  }

  void _registerMethodHandlers() {
    widget.control.addInvokeMethodListener((String name, dynamic args) async {
      switch (name) {
        case "is_available":
          return await _iap.isAvailable();

        case "query_products":
          final List<String> ids = args is Map && args["product_ids"] is List
              ? (args["product_ids"] as List).map((e) => e.toString()).toList()
              : [];
          final ProductDetailsResponse response = await _iap.queryProductDetails(ids.toSet());
          
          final List<Map<String, dynamic>> products = [];
          for (final product in response.productDetails) {
            _cachedProducts[product.id] = product;
            products.add({
              "id": product.id,
              "title": product.title,
              "description": product.description,
              "price": product.price,
              "raw_price": product.rawPrice,
              "currency_code": product.currencyCode,
              "currency_symbol": product.currencySymbol,
            });
          }

          return {
            "products": products,
            "not_found_ids": response.notFoundIDs,
            "error": response.error?.message,
          };

        case "buy_non_consumable":
          final String id = args is Map ? (args["product_id"] as String? ?? "") : args.toString();
          final product = _cachedProducts[id];
          if (product == null) {
            return {"success": false, "error": "Product not found. Query products first."};
          }
          final PurchaseParam param = PurchaseParam(productDetails: product);
          final bool success = await _iap.buyNonConsumable(purchaseParam: param);
          return {"success": success};

        case "buy_consumable":
          final String id = args is Map ? (args["product_id"] as String? ?? "") : args.toString();
          final product = _cachedProducts[id];
          if (product == null) {
            return {"success": false, "error": "Product not found. Query products first."};
          }
          final PurchaseParam param = PurchaseParam(productDetails: product);
          final bool success = await _iap.buyConsumable(purchaseParam: param, autoConsume: true);
          return {"success": success};

        case "restore_purchases":
          await _iap.restorePurchases();
          return true;

        default:
          throw Exception("Unknown in-app purchase method: $name");
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}
