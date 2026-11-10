# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Customer Reference",
    "summary": "Customer Reference (the customer's PO number) on repair orders, "
    "copied to the sale orders created from them.",
    "version": "18.0.1.0.0",
    "category": "Inventory/Repair",
    "author": "Avunu LLC",
    "website": "https://github.com/Avunu/repair-addons",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "repair",
        "sale",
    ],
    "data": [
        "views/repair_order_views.xml",
        "report/report_templates.xml",
    ],
}
