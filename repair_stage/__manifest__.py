# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Stages",
    "summary": "Configurable kanban stages for repair orders, each tied to a "
    "repair status, with drag-and-drop that runs the real status change",
    "version": "18.0.1.0.0",
    "category": "Inventory/Repair",
    "author": "Avunu LLC",
    "website": "https://avu.nu",
    "license": "AGPL-3",
    "depends": ["repair"],
    "data": [
        "security/ir.model.access.csv",
        "data/repair_order_stage_data.xml",
        "views/repair_order_stage_views.xml",
        "views/repair_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "repair_stage/static/src/views/repair_stage_kanban.js",
        ],
        "web.assets_tests": [
            "repair_stage/static/tests/tours/*.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
}
