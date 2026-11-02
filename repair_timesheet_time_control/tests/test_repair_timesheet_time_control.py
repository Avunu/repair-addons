# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


# post_install: creating a project touches fields owned by modules that load
# after this one (sale_timesheet's required billing_type, for one), so the
# registry has to be complete before these run.
@tagged("post_install", "-at_install")
class TestRepairTimesheetTimeControl(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.project = cls.env["project.project"].create(
            {
                "name": "Shop Labor",
                "allow_timesheets": True,
                "company_id": cls.company.id,
            }
        )
        cls.company.repair_timesheet_project_id = cls.project
        cls.technician = new_test_user(
            cls.env,
            login="repair_tech",
            # password_security is installed and rejects the login-as-password
            # that new_test_user defaults to.
            password="Repair-Tech-1!",
            groups="base.group_user,"
            "hr_timesheet.group_hr_timesheet_user,"
            "project.group_project_user,"
            "stock.group_stock_user",
            company_id=cls.company.id,
        )
        cls.env["hr.employee"].create(
            {
                "name": "Repair Tech",
                "user_id": cls.technician.id,
                "company_id": cls.company.id,
            }
        )
        cls.repair = cls.env["repair.order"].create({"name": "RO/TEST/0001"})

    def _repair(self):
        """The repair order as the technician sees it.

        Everything about the timer is per user -- the running line is looked up
        with user_id = current user -- so the tests have to look through the
        technician's eyes, not the superuser's.
        """
        return self.repair.with_user(self.technician)

    def _start_timer(self, repair):
        """Run what the Start Timer button does, wizard included."""
        action = repair.button_start_work()
        wizard_model = (
            self.env["hr.timesheet.switch"]
            .with_user(self.technician)
            .with_context(**action["context"])
        )
        defaults = wizard_model.default_get(list(wizard_model._fields))
        wizard = wizard_model.create(defaults)
        wizard.action_switch()
        return defaults

    def _timesheets(self):
        return self.env["account.analytic.line"].search(
            [("repair_order_id", "=", self.repair.id)], order="id"
        )

    def _backdate(self, line, hours):
        """Make the elapsed time deterministic instead of "a few ms"."""
        line.date_time = fields.Datetime.now() - timedelta(hours=hours)

    def test_start_prefills_project_and_description(self):
        defaults = self._start_timer(self._repair())
        self.assertEqual(defaults["project_id"], self.project.id)
        self.assertEqual(defaults["name"], self.repair.display_name)

    def test_start_logs_a_running_line_on_the_repair_order(self):
        self._start_timer(self._repair())
        lines = self._timesheets()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.project_id, self.project)
        self.assertEqual(lines.unit_amount, 0, "A running timer has no duration yet")
        self.assertTrue(lines.date_time)

    def test_button_flips_to_stop_then_back(self):
        repair = self._repair()
        self.assertEqual(repair.show_time_control, "start")
        self._start_timer(repair)
        repair.invalidate_recordset()
        self.assertEqual(repair.show_time_control, "stop")
        self._backdate(self._timesheets(), 1)
        repair.button_end_work()
        repair.invalidate_recordset()
        self.assertEqual(repair.show_time_control, "start")
        self.assertAlmostEqual(self._timesheets().unit_amount, 1, places=2)

    def test_second_stint_reuses_the_previous_line(self):
        repair = self._repair()
        self._start_timer(repair)
        self._backdate(self._timesheets(), 1)
        repair.button_end_work()
        repair.invalidate_recordset()
        defaults = self._start_timer(repair)
        # The wizard offered the earlier line, so the description carried over
        # and the new timer is a copy of it -- on the same repair order.
        self.assertEqual(defaults["analytic_line_id"], self._timesheets()[0].id)
        lines = self._timesheets()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[1].unit_amount, 0)
        self.assertEqual(lines[1].name, lines[0].name)

    def test_timer_is_per_user(self):
        """A second technician sees Start, not the first one's running timer."""
        other = new_test_user(
            self.env,
            login="repair_tech_2",
            password="Repair-Tech-2!",
            groups="base.group_user,"
            "hr_timesheet.group_hr_timesheet_user,"
            "project.group_project_user,"
            "stock.group_stock_user",
            company_id=self.company.id,
        )
        self.env["hr.employee"].create(
            {
                "name": "Repair Tech 2",
                "user_id": other.id,
                "company_id": self.company.id,
            }
        )
        self._start_timer(self._repair())
        self.assertEqual(self.repair.with_user(other).show_time_control, "start")
