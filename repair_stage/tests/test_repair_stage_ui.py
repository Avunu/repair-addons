# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestRepairStageBoard(HttpCase):
    def test_board_drag_and_drop(self):
        new_test_user(
            self.env,
            login="stage_tour_user",
            groups="base.group_user,stock.group_stock_user",
        )
        Repair = self.env["repair.order"]
        alpha_partner, beta_partner = self.env["res.partner"].create(
            [{"name": "Stage Tour Alpha"}, {"name": "Stage Tour Beta"}]
        )
        alpha = Repair.create({"partner_id": alpha_partner.id})
        alpha._action_repair_confirm()
        beta = Repair.create({"partner_id": beta_partner.id})
        # Stand-in for a Confirm dialog (repair_service_workflow's wizard, or
        # core's insufficient-quantity warning): any window action will do.
        dialog = {
            "type": "ir.actions.act_window",
            "res_model": "repair.order.stage",
            "res_id": self.env.ref("repair_stage.stage_confirmed").id,
            "views": [[False, "form"]],
            "target": "new",
        }
        with patch.object(type(Repair), "action_validate", lambda self: dict(dialog)):
            self.start_tour("/odoo", "repair_stage_board", login="stage_tour_user")

        self.assertEqual(alpha.state, "under_repair")
        self.assertEqual(
            alpha.stage_id, self.env.ref("repair_stage.stage_waiting_parts")
        )
        self.assertEqual(beta.state, "draft")
