# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        # Every route from a repair order to a quotation (core's Create
        # Quotation, repair_order_group, ...) links repair_order_ids here.
        orders._copy_repair_client_order_ref()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if "repair_order_ids" in vals:
            self._copy_repair_client_order_ref()
        return res

    def _copy_repair_client_order_ref(self):
        """Fill an empty Customer Reference from the repair orders behind the order.

        A reference that is already set is never replaced. An order that
        covers several repair orders (repair_order_group) gets each distinct
        reference once, in repair order sequence.
        """
        for order in self.filtered(lambda so: not so.client_order_ref):
            refs = order.sudo().repair_order_ids.sorted("id").mapped("client_order_ref")
            refs = list(dict.fromkeys(ref for ref in refs if ref))
            if refs:
                order.client_order_ref = ", ".join(refs)
