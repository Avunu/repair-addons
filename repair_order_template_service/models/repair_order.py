# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    @api.onchange("repair_order_template_id")
    def _onchange_repair_order_template_id(self):
        res = super()._onchange_repair_order_template_id()
        template = self.repair_order_template_id
        # Mirror the parts behavior: replace existing service lines only when
        # the template defines some.
        if template and template.service_line_ids:
            self.repair_service_ids = [fields.Command.clear()] + [
                fields.Command.create(line._prepare_service_values())
                for line in template.service_line_ids
            ]
        return res
