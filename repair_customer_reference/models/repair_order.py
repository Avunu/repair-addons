# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    # Same field, name and label as sale.order.client_order_ref
    client_order_ref = fields.Char(string="Customer Reference", copy=False)

    def write(self, vals):
        res = super().write(vals)
        if "client_order_ref" in vals:
            # A PO number often arrives after the quotation exists
            self.sale_order_id.sudo()._copy_repair_client_order_ref()
        return res
