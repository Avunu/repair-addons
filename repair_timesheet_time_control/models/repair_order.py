# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class RepairOrder(models.Model):
    _name = "repair.order"
    _inherit = ["repair.order", "hr.timesheet.time_control.mixin"]

    @api.model
    def _relation_with_timesheet_line(self):
        """Field on account.analytic.line that points back at us.

        Added by repair_timesheet; it is the whole reason the generic mixin
        can drive a timer from a repair order.
        """
        return "repair_order_id"

    @api.depends("timesheet_ids.unit_amount", "timesheet_ids.date_time")
    def _compute_show_time_control(self):
        # The mixin declares no dependencies of its own, so without these the
        # button would keep reading "Start" until the form was reloaded.
        return super()._compute_show_time_control()

    def _timesheet_default_project(self):
        """Project the timer logs to when the technician doesn't pick one.

        A timesheet cannot exist without a project: hr_timesheet skips any
        analytic line that has neither project nor task ("It is not a
        timesheet"), and the time control only recognises running lines whose
        project allows timesheets. Configure one company-wide and starting
        work on a repair order becomes a single tap.
        """
        self.ensure_one()
        return self.company_id.repair_timesheet_project_id

    def _timesheet_default_description(self):
        """Prefill the wizard's required Description.

        The vehicle comes from repair_fleet_vehicle, which this module does
        not depend on -- hence the soft check rather than a plain read.

        The name is read with sudo, as the ORM itself does when rendering a
        many2one (Many2one.convert_to_read). Core fleet only lets an Officer
        read vehicles they personally drive, which is never true of customer
        vehicles; a label on a prefilled description is not worth denying a
        technician their timer over. repair_fleet_vehicle relaxes that rule
        properly, but this module does not depend on it.
        """
        self.ensure_one()
        vehicle = self.vehicle_id if "vehicle_id" in self._fields else False
        if vehicle:
            return f"{self.display_name} — {vehicle.sudo().display_name}"
        return self.display_name

    def button_start_work(self):
        result = super().button_start_work()
        result["context"].update(
            {
                "default_project_id": self._timesheet_default_project().id,
                "default_name": self._timesheet_default_description(),
                # Set explicitly rather than relying on the client: the wizard
                # reads these to find the technician's previous stint on this
                # same repair order (see hr.timesheet.switch).
                "active_model": self._name,
                "active_id": self.id,
            }
        )
        return result
