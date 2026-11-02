# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Purchase Order Parts",
    "summary": "Add every part from a purchase order to an existing repair "
    "order in one click, so a repair order can be built before its parts "
    "are on hand - either direction, from the repair order or from the "
    "purchase order/receipt.",
    "version": "18.0.2.0.0",
    "category": "Inventory/Repair",
    "author": "Avunu LLC",
    "website": "https://avu.nu",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        # order_line, product_qty/product_uom, display_type
        "purchase",
        # created_purchase_line_ids on stock.move, and the Purchases /
        # Repair Orders smart buttons that read it (purchase_repair is
        # auto_install with repair + purchase_stock, so it's normally
        # already present, but depending on it directly is what actually
        # guarantees it for this feature).
        "purchase_repair",
    ],
    "data": [
        "views/purchase_order_views.xml",
        "views/repair_order_views.xml",
        "views/stock_picking_views.xml",
    ],
}
