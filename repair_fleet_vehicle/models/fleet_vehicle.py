# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    # Base fleet searches name and driver; also match the customer's unit number.
    _rec_names_search = ["name", "driver_id.name", "unit_number"]

    repair_order_ids = fields.One2many(
        "repair.order", "vehicle_id", string="Repair Orders"
    )
    repair_count = fields.Integer(compute="_compute_repair_count")
    unit_number = fields.Char(
        tracking=True,
        copy=False,
        help="The customer's own fleet number for this vehicle, as painted "
        "on the truck or used on their work orders (e.g. T-104).",
    )

    @api.depends_context("show_vehicle_year")
    @api.depends("model_year", "unit_number")
    def _compute_display_name(self):
        """Add the model year and unit number when a form asks for them.

        Only the label changes (``name`` is a stored compute shared by every
        picker), so callers opt in with ``show_vehicle_year`` in the field's
        context. Result: ``2016 Freightliner/Cascadia/TRK-1234 (T-104)``.
        """
        super()._compute_display_name()
        if not self.env.context.get("show_vehicle_year"):
            return
        for vehicle in self:
            label = vehicle.display_name
            if vehicle.model_year:
                label = f"{vehicle.model_year} {label}"
            if vehicle.unit_number:
                label = f"{label} ({vehicle.unit_number})"
            vehicle.display_name = label

    def _compute_repair_count(self):
        counts = dict(
            self.env["repair.order"]._read_group(
                [("vehicle_id", "in", self.ids)], ["vehicle_id"], ["__count"]
            )
        )
        for vehicle in self:
            vehicle.repair_count = counts.get(vehicle, 0)

    def action_view_repairs(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "repair.action_repair_order_tree"
        )
        action["domain"] = [("vehicle_id", "=", self.id)]
        action["context"] = {
            "default_vehicle_id": self.id,
            "default_partner_id": (self.owner_id or self.driver_id).id,
        }
        return action
