# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        index=True,
    )

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.vehicle_id:
            vals["vehicle_id"] = self.vehicle_id.id
        return vals
