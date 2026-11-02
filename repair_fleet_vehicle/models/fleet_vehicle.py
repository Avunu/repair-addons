# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

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
