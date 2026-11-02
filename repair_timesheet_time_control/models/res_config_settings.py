# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    repair_timesheet_project_id = fields.Many2one(
        related="company_id.repair_timesheet_project_id",
        readonly=False,
    )
