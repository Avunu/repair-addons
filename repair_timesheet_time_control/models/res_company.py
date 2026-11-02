# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    repair_timesheet_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Repair Labor Project",
        domain="[('allow_timesheets', '=', True)]",
        help="Project the repair order timer logs to. Timesheet lines always "
        "belong to a project, so leaving this empty means technicians have to "
        "pick one every time they start work.",
    )
