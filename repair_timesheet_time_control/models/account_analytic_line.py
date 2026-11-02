# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def default_get(self, fields_list):
        """Normalise fields_list to a list.

        Two OCA modules in this stack disagree about the type:
        project_timesheet_time_control's hr.timesheet.switch.action_switch
        hands default_get a ``dict_keys`` (``_fields.keys()``), while
        hr_timesheet_time_control_begin_end's override does
        ``fields_list + ["product_uom_id"]``, which only works on a list.

        The result is a TypeError the first time a technician starts a timer
        on a record with no earlier line to resume -- the resume path copies
        an existing line instead and never calls default_get, so it only
        breaks the very first stint.
        """
        return super().default_get(list(fields_list))
