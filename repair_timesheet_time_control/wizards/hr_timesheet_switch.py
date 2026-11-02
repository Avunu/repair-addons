# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    @api.model
    def _closest_suggestion(self):
        """Carry over this technician's last stint on the same repair order.

        The base wizard only recognises timesheet lines, tasks and projects,
        so a repair order came up blank -- including the second time a
        technician picked the same job back up. Reusing their previous line
        keeps the description and project, and makes the new timer a copy of
        it (so it lands on this repair order too).
        """
        context = self.env.context
        if context.get("active_model") == "repair.order" and context.get("active_id"):
            return self.env["account.analytic.line"].search(
                [
                    ("employee_id", "in", self.env.user.employee_ids.ids),
                    ("repair_order_id", "=", context["active_id"]),
                ],
                order="date_time DESC",
                limit=1,
            )
        return super()._closest_suggestion()
