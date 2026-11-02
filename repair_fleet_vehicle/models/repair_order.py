# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        index=True,
        tracking=True,
    )
    show_all_vehicles = fields.Boolean(
        string="Any Owner",
        help="Search vehicles of any owner instead of only the customer's.",
    )
    vehicle_license_plate = fields.Char(
        related="vehicle_id.license_plate",
        string="License Plate",
        store=True,
    )
    vehicle_vin = fields.Char(
        related="vehicle_id.vin_sn",
        string="VIN",
        store=True,
    )
    vehicle_odometer_unit = fields.Selection(related="vehicle_id.odometer_unit")
    odometer_in = fields.Float(
        string="Odometer In",
        help="Odometer reading when the vehicle arrived at the shop. "
        "Logged to the vehicle's odometer history when the repair is confirmed.",
    )
    customer_concern = fields.Html(
        string="Customer Concern",
        help="The issue as reported by the customer.",
    )

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        for repair in self:
            if repair.vehicle_id and not repair.partner_id:
                repair.partner_id = (
                    repair.vehicle_id.owner_id or repair.vehicle_id.driver_id
                )

    def _action_repair_confirm(self):
        res = super()._action_repair_confirm()
        self._log_vehicle_odometer()
        return res

    def _log_vehicle_odometer(self):
        odometer_vals = [
            {"vehicle_id": repair.vehicle_id.id, "value": repair.odometer_in}
            for repair in self
            if repair.vehicle_id
            and repair.odometer_in
            and repair.vehicle_id.odometer != repair.odometer_in
        ]
        if odometer_vals:
            self.env["fleet.vehicle.odometer"].create(odometer_vals)

    def action_create_sale_order(self):
        res = super().action_create_sale_order()
        for repair in self:
            if repair.vehicle_id and repair.sale_order_id:
                repair.sale_order_id.vehicle_id = repair.vehicle_id
        return res
