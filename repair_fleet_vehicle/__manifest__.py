# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Fleet Vehicle",
    "summary": "Link repair orders to customer vehicles (fleet), with odometer "
    "capture, customer concern, and vehicle info on estimates and invoices.",
    "version": "18.0.1.1.1",
    "category": "Inventory/Repair",
    "author": "Avunu LLC",
    "website": "https://avu.nu",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "repair",
        # Brings fleet + the partner-as-owner link used to filter vehicles
        # by customer and to fill the customer from the vehicle.
        "fleet_vehicle_ownership",
    ],
    "data": [
        "security/fleet_security.xml",
        "views/repair_order_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "report/report_templates.xml",
    ],
}
