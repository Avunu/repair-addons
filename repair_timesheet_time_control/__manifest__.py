# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Timesheet Time Control",
    "summary": "Start/stop the work timer from a repair order, logging to the "
    "repair order's timesheets",
    "version": "18.0.1.0.0",
    "category": "Inventory/Repair",
    "author": "Avunu LLC",
    "website": "https://avu.nu",
    "license": "AGPL-3",
    # repair_timesheet carries account.analytic.line.repair_order_id, which is
    # the back-link the time control mixin needs; project_timesheet_time_control
    # carries the timer itself.
    "depends": [
        "repair_timesheet",
        "project_timesheet_time_control",
        "base_repair_config",
    ],
    "data": [
        "views/repair_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
