# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RepairOrderStage(models.Model):
    """A kanban column for repair orders.

    Same shape as project.task.type / maintenance.stage, plus ``state``: the
    core repair status the stage belongs to. Several stages may share one
    status ("Confirmed", "Waiting for Customer" and "Waiting for Parts" are
    all ``confirmed``); the core workflow only ever looks at the status.
    """

    _name = "repair.order.stage"
    _description = "Repair Order Stage"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        selection="_selection_state",
        string="Status",
        required=True,
        help="The repair status this stage belongs to. Moving an order into "
        "a stage of another status runs that status change (Confirm, Start "
        "Repair, End Repair), exactly as the buttons on the order do.",
    )
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="Show this stage as a collapsed column on the repairs board.",
    )
    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)

    @api.model
    def _selection_state(self):
        return (
            self.env["repair.order"]._fields["state"]._description_selection(self.env)
        )

    # Every status needs somewhere to land: when a button changes an order's
    # status, the order moves to the first stage of that status.

    def write(self, vals):
        if "state" not in vals and vals.get("active", True):
            return super().write(vals)
        states = set(self.mapped("state"))
        res = super().write(vals)
        self._check_states_keep_a_stage(states)
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_except_last_stage_of_state(self):
        for state in set(self.mapped("state")):
            if not self.search_count(
                [("state", "=", state), ("id", "not in", self.ids)], limit=1
            ):
                raise UserError(self._last_stage_message(state))

    def _check_states_keep_a_stage(self, states):
        for state in states:
            if not self.search_count([("state", "=", state)], limit=1):
                raise UserError(self._last_stage_message(state))

    def _last_stage_message(self, state):
        label = dict(self._selection_state())[state]
        return _(
            "Every repair status needs at least one active stage, and this is "
            "the last one for “%(status)s”.",
            status=label,
        )
