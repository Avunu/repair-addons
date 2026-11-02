# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Moving an order into a stage of a later status is the same as pressing the
# button for that step. Only the forward steps a button exists for are
# allowed; skipping a step or cancelling has to be done with the buttons.
STAGE_TRANSITIONS = {
    ("draft", "confirmed"): "action_validate",
    ("confirmed", "under_repair"): "action_repair_start",
    ("under_repair", "done"): "action_repair_end",
}

# The statuses in workflow order. An open order can be moved back to a stage
# of an earlier status (e.g. Under Repair → Waiting for Parts when a part
# turns out to be missing): that only relabels it, its status stays as is.
STATE_SEQUENCE = ["draft", "confirmed", "under_repair", "done"]
OPEN_STATES = ("draft", "confirmed", "under_repair")

# When a step opens a dialog (Confirm/Finalize wizards), the stage the order
# was dropped on rides along in the context so the order lands there, rather
# than in the first stage of its new status, once the dialog completes.
TARGET_STAGE_KEY = "repair_stage_target_id"
TARGET_REPAIR_KEY = "repair_stage_target_res_id"


class RepairOrder(models.Model):
    _inherit = "repair.order"

    stage_id = fields.Many2one(
        "repair.order.stage",
        string="Stage",
        compute="_compute_stage_id",
        store=True,
        readonly=False,
        index=True,
        copy=False,
        tracking=True,
        ondelete="restrict",
        group_expand="_read_group_stage_ids",
    )

    # Only runs when the status actually changes (see _write_state), so an
    # order moved back to an earlier stage moves on with its next step.
    # The dropped-on stage is applied here rather than written alongside the
    # status: Automation Rules only see stage changes made by a stage write
    # or by this compute.
    @api.depends("state")
    def _compute_stage_id(self):
        target = self.env["repair.order.stage"].browse(
            self.env.context.get(TARGET_STAGE_KEY)
        )
        target_repair_id = self.env.context.get(TARGET_REPAIR_KEY)
        first_stage = {}
        for repair in self:
            if repair.stage_id.state == repair.state:
                repair.stage_id = repair.stage_id
            elif repair.id == target_repair_id and target.state == repair.state:
                repair.stage_id = target
            else:
                if repair.state not in first_stage:
                    first_stage[repair.state] = self.env["repair.order.stage"].search(
                        [("state", "=", repair.state)], limit=1
                    )
                repair.stage_id = first_stage[repair.state]

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return stages.search([])

    @api.constrains("stage_id", "state")
    def _check_stage_matches_state(self):
        for repair in self:
            stage = repair.stage_id
            if stage and stage.state != repair.state and not repair._is_behind(stage):
                raise UserError(
                    _(
                        "The stage “%(stage)s” doesn't fit the status of %(order)s.",
                        stage=stage.name,
                        order=repair.name,
                    )
                )

    def _is_behind(self, stage):
        """Whether ``stage`` belongs to an earlier status than this open order."""
        self.ensure_one()
        if self.state not in OPEN_STATES or stage.state not in STATE_SEQUENCE:
            return False
        return STATE_SEQUENCE.index(stage.state) < STATE_SEQUENCE.index(self.state)

    @api.model_create_multi
    def create(self, vals_list):
        # A kanban column passes its stage as a default; drop it when it
        # belongs to another status and let the compute pick the stage.
        stage_model = self.env["repair.order.stage"]
        default_state = self.default_get(["state"]).get("state")
        for vals in vals_list:
            if vals.get("stage_id"):
                stage = stage_model.browse(vals["stage_id"])
                if stage.state != vals.get("state", default_state):
                    del vals["stage_id"]
        return super().create(vals_list)

    def write(self, vals):
        if "state" in vals:
            if "stage_id" in vals:
                return super().write(vals)
            return self._write_state(vals)
        if "stage_id" not in vals:
            return super().write(vals)
        stage = self.env["repair.order.stage"].browse(vals["stage_id"])
        if not stage:
            raise UserError(_("A repair order must have a stage."))
        crossing = self.filtered(
            lambda repair: repair.state != stage.state and not repair._is_behind(stage)
        )
        if not crossing:
            return super().write(vals)
        # Save everything else first: a step may depend on it (e.g. the
        # technician set in the same save).
        res = super(RepairOrder, self - crossing).write(vals)
        other_vals = {key: val for key, val in vals.items() if key != "stage_id"}
        if other_vals:
            super(RepairOrder, crossing).write(other_vals)
        for repair in crossing:
            if isinstance(repair._run_stage_transition(stage), dict):
                raise UserError(
                    _(
                        "Moving %(order)s to “%(stage)s” needs a confirmation "
                        "dialog. Use the button on the repair order, or drag "
                        "it on the repairs board.",
                        order=repair.name,
                        stage=stage.name,
                    )
                )
        return res

    def _write_state(self, vals):
        # Rewriting an order's current status changes nothing, but Odoo would
        # still recompute stage_id and pull an order that was moved back to an
        # earlier stage forward again. Only write the status where it changes.
        unchanged = self.filtered(lambda repair: repair.state == vals["state"])
        if not unchanged:
            return super().write(vals)
        res = super(RepairOrder, self - unchanged).write(vals)
        other_vals = {key: val for key, val in vals.items() if key != "state"}
        if other_vals:
            super(RepairOrder, unchanged).write(other_vals)
        return res

    def action_set_stage(self, stage_id):
        """Move to a stage, running the status change it implies.

        Called by the repairs board when a card is dropped on another column.
        Returns True, or the action of a dialog the step needs.
        """
        self.ensure_one()
        stage = self.env["repair.order.stage"].browse(stage_id).exists()
        if not stage:
            raise UserError(_("That stage no longer exists."))
        if stage.state == self.state or self._is_behind(stage):
            self.stage_id = stage
            return True
        return self._run_stage_transition(stage)

    def _run_stage_transition(self, stage):
        self.ensure_one()
        method = STAGE_TRANSITIONS.get((self.state, stage.state))
        if not method:
            raise UserError(self._blocked_move_message(stage))
        target_ctx = {TARGET_STAGE_KEY: stage.id, TARGET_REPAIR_KEY: self.id}
        result = getattr(self.with_context(**target_ctx), method)()
        if isinstance(result, dict) and isinstance(result.get("context"), dict):
            result = dict(result, context=dict(result["context"], **target_ctx))
        return result

    def _blocked_move_message(self, stage):
        if self.state not in OPEN_STATES:
            return _(
                "%(order)s is already finished, so it can't be moved to “%(stage)s”.",
                order=self.name,
                stage=stage.name,
            )
        labels = dict(self._fields["state"]._description_selection(self.env))
        return _(
            "%(order)s can't move from “%(from)s” to “%(to)s” here. Orders move "
            "one step forward at a time (New → Confirmed → Under Repair → "
            "Repaired) or back to any earlier stage; use the buttons on the "
            "repair order for anything else.",
            order=self.name,
            **{"from": labels[self.state], "to": labels[stage.state]},
        )
