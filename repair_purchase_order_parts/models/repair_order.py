# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import UserError


class RepairOrder(models.Model):
    _inherit = "repair.order"

    @api.model_create_multi
    def create(self, vals_list):
        """A repair order created from the purchase order's "Create New
        Repair" picker (PurchaseOrder.action_add_to_repair's list view, with
        create enabled) carries `po_id` in its creation context - the same
        key action_select_po_for_repair reads for an *existing* repair
        order - so the new repair order gets that purchase order's parts
        added automatically instead of the picker's flow silently doing
        nothing for a record nobody explicitly picked a source for.
        """
        records = super().create(vals_list)
        po = self.env["purchase.order"].browse(self.env.context.get("po_id"))
        if po:
            for repair in records:
                move_vals = po._prepare_repair_move_vals(repair, [])
                if move_vals:
                    self.env["stock.move"].create(move_vals)
        return records

    def action_add_parts_from_purchase_order(self):
        """Open a purchase order picker for this repair order.

        Clicking a purchase order row there (see PurchaseOrder.
        action_select_for_repair) adds every product line on it to this
        repair order's Parts as an 'add' move, mirroring how the built-in
        Catalog button on the same list adds parts - the difference is the
        parts come from a purchase order (e.g. one built by an EDI/PDF
        import) instead of the product catalog, which is what lets a
        repair order be built before its parts have been purchased.
        """
        self.ensure_one()
        if self.state in ("done", "cancel"):
            raise UserError(
                _("Parts can't be added to a %s repair order.", self.state)
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Select a Purchase Order"),
            "res_model": "purchase.order",
            "view_mode": "list",
            "views": [
                (
                    self.env.ref(
                        "repair_purchase_order_parts."
                        "view_purchase_order_list_select_for_repair"
                    ).id,
                    "list",
                )
            ],
            "target": "new",
            "domain": [
                ("state", "!=", "cancel"),
                ("company_id", "=", self.company_id.id),
            ],
            "context": {"repair_id": self.id},
        }

    def action_select_po_for_repair(self):
        """Row-click action on the purchase order's repair order picker
        (see PurchaseOrder.action_add_to_repair): add every product line on
        that purchase order to this repair order's Parts.

        Shares PurchaseOrder._prepare_repair_move_vals with the Repair ->
        PO direction (action_select_for_repair /
        action_add_selected_to_repair) so the two directions can't drift
        apart on what a "part from a purchase order" move looks like.
        """
        self.ensure_one()
        po = self.env["purchase.order"].browse(self.env.context.get("po_id"))
        if not po:
            raise UserError(_("No purchase order to add parts from."))
        already_linked = self.move_ids.created_purchase_line_ids.ids
        move_vals = po._prepare_repair_move_vals(self, already_linked)
        if not move_vals:
            raise UserError(
                _("Every part on %s is already on this repair order.", po.name)
            )
        self.env["stock.move"].create(move_vals)
        return {"type": "ir.actions.act_window_close"}
