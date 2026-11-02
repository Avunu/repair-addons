# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        index=True,
    )
