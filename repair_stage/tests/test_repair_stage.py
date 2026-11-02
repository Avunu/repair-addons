# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, tagged

WIZARD_ACTION = {
    "type": "ir.actions.act_window",
    "res_model": "res.partner",
    "target": "new",
    "context": {"some_key": 1},
}


@tagged("post_install", "-at_install")
class TestRepairStage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Stage = cls.env["repair.order.stage"]
        cls.stage_new = cls.env.ref("repair_stage.stage_new")
        cls.stage_confirmed = cls.env.ref("repair_stage.stage_confirmed")
        cls.stage_waiting_customer = cls.env.ref("repair_stage.stage_waiting_customer")
        cls.stage_waiting_parts = cls.env.ref("repair_stage.stage_waiting_parts")
        cls.stage_under_repair = cls.env.ref("repair_stage.stage_under_repair")
        cls.stage_repaired = cls.env.ref("repair_stage.stage_repaired")
        cls.partner = cls.env["res.partner"].create({"name": "Acme Trucking"})
        cls.RepairOrder = type(cls.env["repair.order"])

    def _repair(self, **vals):
        return self.env["repair.order"].create(dict(partner_id=self.partner.id, **vals))

    def _confirmed_repair(self):
        repair = self._repair()
        repair._action_repair_confirm()
        return repair

    # -- stage follows status ----------------------------------------------

    def test_new_order_starts_in_first_draft_stage(self):
        self.assertEqual(self._repair().stage_id, self.stage_new)

    def test_buttons_move_to_first_stage_of_new_status(self):
        repair = self._confirmed_repair()
        self.assertEqual(repair.stage_id, self.stage_confirmed)
        repair.action_repair_start()
        self.assertEqual(repair.stage_id, self.stage_under_repair)
        repair.action_repair_done()
        self.assertEqual(repair.stage_id, self.stage_repaired)

    def test_first_stage_follows_column_order(self):
        self.stage_waiting_parts.sequence = 1
        repair = self._confirmed_repair()
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)

    def test_status_change_keeps_stage_of_same_status(self):
        repair = self._confirmed_repair()
        repair.stage_id = self.stage_waiting_parts
        repair.write({"state": "confirmed"})
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)

    def test_create_drops_column_default_of_other_status(self):
        repair = self._repair(stage_id=self.stage_waiting_parts.id)
        self.assertEqual(repair.state, "draft")
        self.assertEqual(repair.stage_id, self.stage_new)

    # -- moving between stages ---------------------------------------------

    def test_same_status_move_only_changes_stage(self):
        repair = self._confirmed_repair()
        self.assertIs(repair.action_set_stage(self.stage_waiting_parts.id), True)
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)
        self.assertEqual(repair.state, "confirmed")

    def test_move_runs_start_repair(self):
        repair = self._confirmed_repair()
        repair.stage_id = self.stage_waiting_parts
        self.assertIs(repair.action_set_stage(self.stage_under_repair.id), True)
        self.assertEqual(repair.state, "under_repair")
        self.assertEqual(repair.stage_id, self.stage_under_repair)

    def test_write_runs_start_repair(self):
        """The form's status bar saves the stage with a plain write."""
        repair = self._confirmed_repair()
        repair.write({"stage_id": self.stage_under_repair.id})
        self.assertEqual(repair.state, "under_repair")

    def test_move_lands_in_dropped_column(self):
        repair = self._repair()
        # Confirm without the dialog other modules put in front of it.
        with patch.object(
            self.RepairOrder,
            "action_validate",
            lambda self: self._action_repair_confirm(),
        ):
            self.assertIs(repair.action_set_stage(self.stage_waiting_parts.id), True)
        self.assertEqual(repair.state, "confirmed")
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)

    def test_dialog_step_returns_action_carrying_target(self):
        repair = self._repair()
        with patch.object(
            self.RepairOrder, "action_validate", lambda self: dict(WIZARD_ACTION)
        ):
            action = repair.action_set_stage(self.stage_waiting_customer.id)
        self.assertEqual(action["res_model"], "res.partner")
        self.assertEqual(action["context"]["some_key"], 1)
        self.assertEqual(repair.state, "draft")
        # The wizard's button runs with the action's context, so the
        # confirmation it makes lands the order in the dropped column.
        repair.with_context(**action["context"])._action_repair_confirm()
        self.assertEqual(repair.stage_id, self.stage_waiting_customer)

    def test_target_only_applies_to_its_own_order(self):
        repair, other = self._repair(), self._repair()
        (repair | other).with_context(
            repair_stage_target_id=self.stage_waiting_parts.id,
            repair_stage_target_res_id=repair.id,
        )._action_repair_confirm()
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)
        self.assertEqual(other.stage_id, self.stage_confirmed)

    def test_write_refuses_dialog_step(self):
        repair = self._repair()
        with (
            patch.object(
                self.RepairOrder, "action_validate", lambda self: dict(WIZARD_ACTION)
            ),
            self.assertRaisesRegex(UserError, "confirmation dialog"),
        ):
            repair.write({"stage_id": self.stage_confirmed.id})

    def test_skipping_a_step_is_blocked(self):
        repair = self._repair()
        with self.assertRaisesRegex(UserError, "one step forward"):
            repair.action_set_stage(self.stage_under_repair.id)
        self.assertEqual(repair.state, "draft")

    # -- moving back ------------------------------------------------------

    def _repair_under_repair(self):
        repair = self._confirmed_repair()
        repair.action_repair_start()
        return repair

    def test_moving_back_keeps_status(self):
        repair = self._repair_under_repair()
        self.assertIs(repair.action_set_stage(self.stage_waiting_parts.id), True)
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)
        self.assertEqual(repair.state, "under_repair")

    def test_write_moves_back(self):
        """The form's status bar saves the stage with a plain write."""
        repair = self._repair_under_repair()
        repair.write({"stage_id": self.stage_new.id})
        self.assertEqual(repair.stage_id, self.stage_new)
        self.assertEqual(repair.state, "under_repair")

    def test_moved_back_order_stays_put_on_status_rewrite(self):
        repair = self._repair_under_repair()
        repair.action_set_stage(self.stage_waiting_parts.id)
        repair.write({"state": "under_repair", "priority": "1"})
        self.assertEqual(repair.stage_id, self.stage_waiting_parts)
        self.assertEqual(repair.priority, "1")

    def test_moved_back_order_returns_to_its_status_stage(self):
        repair = self._repair_under_repair()
        repair.action_set_stage(self.stage_waiting_parts.id)
        self.assertIs(repair.action_set_stage(self.stage_under_repair.id), True)
        self.assertEqual(repair.stage_id, self.stage_under_repair)
        self.assertEqual(repair.state, "under_repair")

    def test_moved_back_order_moves_on_with_next_step(self):
        repair = self._repair_under_repair()
        repair.action_set_stage(self.stage_waiting_parts.id)
        repair.action_repair_done()
        self.assertEqual(repair.stage_id, self.stage_repaired)

    def test_moved_back_order_can_be_dropped_on_next_step(self):
        repair = self._repair_under_repair()
        repair.action_set_stage(self.stage_waiting_parts.id)
        with patch.object(
            self.RepairOrder,
            "action_repair_end",
            lambda self: self.action_repair_done(),
        ):
            self.assertIs(repair.action_set_stage(self.stage_repaired.id), True)
        self.assertEqual(repair.state, "done")
        self.assertEqual(repair.stage_id, self.stage_repaired)

    def test_finished_order_cannot_move_back(self):
        repair = self._repair_under_repair()
        repair.action_repair_done()
        with self.assertRaisesRegex(UserError, "already finished"):
            repair.action_set_stage(self.stage_under_repair.id)
        self.assertEqual(repair.stage_id, self.stage_repaired)

    def test_cannot_move_into_cancelled(self):
        repair = self._repair_under_repair()
        with self.assertRaisesRegex(UserError, "one step forward"):
            repair.action_set_stage(self.env.ref("repair_stage.stage_cancelled").id)
        self.assertEqual(repair.state, "under_repair")

    def test_stage_must_match_status(self):
        repair = self._repair()
        with self.assertRaises(UserError):
            repair.write({"state": "draft", "stage_id": self.stage_waiting_parts.id})

    # -- stage configuration -----------------------------------------------

    def test_board_shows_every_stage(self):
        groups = self.env["repair.order"].read_group(
            [("id", "=", 0)], ["stage_id"], ["stage_id"]
        )
        self.assertEqual(
            [group["stage_id"][0] for group in groups], self.Stage.search([]).ids
        )

    def test_cannot_archive_last_stage_of_a_status(self):
        with self.assertRaisesRegex(UserError, "last one"):
            self.stage_new.active = False

    def test_cannot_move_last_stage_to_other_status(self):
        with self.assertRaisesRegex(UserError, "last one"):
            self.stage_under_repair.state = "confirmed"

    def test_can_archive_one_of_several_stages(self):
        self.stage_waiting_customer.active = False
        self.assertFalse(self.stage_waiting_customer.active)

    def test_cannot_delete_last_stage_of_a_status(self):
        stage = self.Stage.create({"name": "Unused", "state": "cancel"})
        stage.unlink()
        with self.assertRaisesRegex(UserError, "last one"):
            self.env.ref("repair_stage.stage_cancelled").unlink()

    # -- automation rules --------------------------------------------------

    def _stage_rule(self, stage, code):
        if "base.automation" not in self.env:
            self.skipTest("base_automation is not installed")
        rule_form = Form(self.env["base.automation"])
        rule_form.name = f"On {stage.name}"
        rule_form.model_id = self.env["ir.model"]._get("repair.order")
        rule_form.trigger = "on_stage_set"
        rule_form.trg_field_ref = stage.id
        rule = rule_form.save()
        # Rules patch repair.order's methods; deleting the rule unpatches them.
        self.addCleanup(rule.unlink)
        stage_field = self.env["ir.model.fields"]._get("repair.order", "stage_id")
        self.assertEqual(rule.trigger_field_ids, stage_field)
        self.env["ir.actions.server"].create(
            {
                "name": "Flag",
                "base_automation_id": rule.id,
                "model_id": rule.model_id.id,
                "state": "code",
                "code": code,
            }
        )
        return rule

    def test_stage_rule_fires_on_move(self):
        self._stage_rule(self.stage_waiting_parts, "record.write({'priority': '1'})")
        repair = self._confirmed_repair()
        self.assertEqual(repair.priority, "0")
        repair.action_set_stage(self.stage_waiting_parts.id)
        self.assertEqual(repair.priority, "1")

    def test_stage_rule_fires_after_dialog_confirm(self):
        """Dropped New → Waiting for Customer, then confirmed in the dialog."""
        self._stage_rule(self.stage_waiting_customer, "record.write({'priority': '1'})")
        repair = self._repair()
        repair.with_context(
            repair_stage_target_id=self.stage_waiting_customer.id,
            repair_stage_target_res_id=repair.id,
        )._action_repair_confirm()
        self.assertEqual(repair.stage_id, self.stage_waiting_customer)
        self.assertEqual(repair.priority, "1")

    def test_stage_rule_fires_on_button(self):
        self._stage_rule(self.stage_under_repair, "record.write({'priority': '1'})")
        repair = self._confirmed_repair()
        repair.action_repair_start()
        self.assertEqual(repair.priority, "1")
