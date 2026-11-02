# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_add_to_repair(self):
        """Same picker as the purchase order's own Add to Repair button
        (see PurchaseOrder.action_add_to_repair), reached from this
        receipt once it's been validated - `purchase_id` is the related
        purchase order core's purchase_stock already puts on every
        incoming picking.
        """
        self.ensure_one()
        return self.purchase_id.action_add_to_repair()
