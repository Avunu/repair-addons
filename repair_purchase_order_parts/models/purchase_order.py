# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import Command, _, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_add_to_repair(self):
        """Open a repair order picker for this purchase order - the mirror
        of RepairOrder.action_add_parts_from_purchase_order below. Clicking
        a repair order row there (see RepairOrder.action_select_po_for_repair)
        adds every product line on this purchase order to that repair
        order's Parts, the same way the Repair -> PO picker does it, just
        starting from the other document.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Select a Repair Order"),
            "res_model": "repair.order",
            "view_mode": "list",
            "views": [
                (
                    self.env.ref(
                        "repair_purchase_order_parts."
                        "view_repair_order_list_select_for_po"
                    ).id,
                    "list",
                )
            ],
            "target": "new",
            "domain": [
                ("state", "not in", ("done", "cancel")),
                ("company_id", "=", self.company_id.id),
            ],
            "context": {"po_id": self.id},
        }

    def action_select_for_repair(self):
        """Row-click action on the repair order's purchase order picker
        (see RepairOrder.action_add_parts_from_purchase_order): add every
        product line on this purchase order to the repair order named in
        context as a part to add.

        Each new part's created_purchase_line_ids is set to the source
        purchase.order.line - the same field Odoo's own Buy-route
        replenishment sets when it generates a PO from a repair order's
        demand - so the stock/repair "Purchases"/"Repair Orders" smart
        buttons connect the two documents whether or not this purchase
        order actually came from that replenishment.
        """
        self.ensure_one()
        repair = self._get_repair_from_context()
        move_vals = self._prepare_repair_move_vals(
            repair, repair.move_ids.created_purchase_line_ids.ids
        )
        if not move_vals:
            raise UserError(
                _("Every part on %s is already on this repair order.", self.name)
            )
        self.env["stock.move"].create(move_vals)
        return {"type": "ir.actions.act_window_close"}

    def action_add_selected_to_repair(self):
        """Header button on the same picker (shown once 1+ rows are
        checked, next to the "N selected" indicator), for adding several
        purchase orders' parts in one go via the list's own checkbox
        selection - `self` here is every checked row, not one. The
        row-click action_select_for_repair() above stays the single-PO
        path (still ensure_one()'d), since a plain row click is still a
        valid way to use this picker too.
        """
        repair = self._get_repair_from_context()
        already_linked = repair.move_ids.created_purchase_line_ids.ids
        move_vals = []
        for po in self:
            move_vals += po._prepare_repair_move_vals(repair, already_linked)
        if not move_vals:
            raise UserError(
                _(
                    "Every part on the selected purchase orders is already "
                    "on this repair order."
                )
            )
        self.env["stock.move"].create(move_vals)
        return {"type": "ir.actions.act_window_close"}

    def _get_repair_from_context(self):
        repair = self.env["repair.order"].browse(self.env.context.get("repair_id"))
        if not repair:
            raise UserError(_("No repair order to add these parts to."))
        return repair

    def _prepare_repair_move_vals(self, repair, already_linked):
        """The stock.move create-vals for this purchase order's own lines
        that aren't already linked to `repair` - shared by the single-PO
        and multi-select add actions above so they can't drift apart.
        """
        self.ensure_one()
        move_vals = []
        for line in self.order_line:
            if line.display_type or not line.product_id or line.id in already_linked:
                continue
            move_vals.append(
                {
                    "repair_id": repair.id,
                    "repair_line_type": "add",
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.product_qty,
                    "product_uom": line.product_uom.id,
                    "location_id": repair.location_id.id,
                    "location_dest_id": repair.location_dest_id.id,
                    "company_id": repair.company_id.id,
                    "date": repair.schedule_date or fields.Datetime.now(),
                    "created_purchase_line_ids": [Command.link(line.id)],
                }
            )
        return move_vals
