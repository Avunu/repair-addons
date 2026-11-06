# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_add_from_purchase_order_repair(self):
        """Control-row button in the repair order's Parts list.

        Mirrors the core action_add_from_catalog_repair trampoline: a
        control-row button's `self` is an empty stock.move recordset, so
        the parent repair order is resolved from context instead.
        """
        repair_order = self.env["repair.order"].browse(self.env.context.get("order_id"))
        return repair_order.action_add_parts_from_purchase_order()
