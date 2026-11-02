# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Order Template Services",
    "summary": "Let repair order templates carry service (labor) lines, so a "
    "template can pre-fill diagnostic fees and book-time labor.",
    "version": "18.0.1.0.0",
    "category": "Inventory/Repair",
    "author": "Avunu LLC",
    "website": "https://avu.nu",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "repair_order_template",
        "repair_service",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/repair_order_template_views.xml",
        "views/repair_order_views.xml",
    ],
}
