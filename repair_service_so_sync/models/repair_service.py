# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

SYNCED_FIELDS = ("product_id", "product_uom", "product_uom_qty", "display_name")


class RepairService(models.Model):
    _inherit = "repair.service"

    sale_line_id = fields.Many2one(
        "sale.order.line",
        string="Sale Order Line",
        copy=False,
    )

    def _create_repair_sale_order_line(self):
        # Deliberately does not call super(): the base (OCA repair_service)
        # implementation batch-creates the lines without keeping a link back,
        # which makes later synchronization impossible. Same vals, created
        # per record so sale_line_id can be stored.
        for service in self:
            if (
                service.sale_line_id
                or not service.repair_id.sale_order_id
                or service.repair_id.sale_order_id.state == "cancel"
            ):
                continue
            vals = service._prepare_sale_order_line_vals(service.product_uom_qty)
            service.sale_line_id = self.env["sale.order.line"].create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        services = super().create(vals_list)
        # Services created after the quotation exists sync immediately
        # (mirrors stock.move.create for parts).
        services.filtered(
            lambda s: s.repair_id.sale_order_id
        )._create_repair_sale_order_line()
        return services

    def write(self, vals):
        res = super().write(vals)
        if any(fname in vals for fname in SYNCED_FIELDS):
            self._update_repair_sale_order_line(vals)
        return res

    def unlink(self):
        # Mirror parts behavior (_clean_repair_sale_order_line): zero the
        # quantity instead of deleting, so confirmed orders keep their audit
        # trail.
        self.sale_line_id.filtered(lambda line: line.order_id.state != "cancel").write(
            {"product_uom_qty": 0.0}
        )
        return super().unlink()

    def _update_repair_sale_order_line(self, vals):
        for service in self:
            line = service.sale_line_id
            if not line or line.order_id.state == "cancel":
                continue
            line_vals = {}
            if "product_id" in vals:
                new_vals = service._prepare_sale_order_line_vals(
                    service.product_uom_qty
                )
                new_vals.pop("order_id", None)
                line_vals.update(new_vals)
            else:
                if "product_uom_qty" in vals:
                    line_vals["product_uom_qty"] = service.product_uom_qty
                if "product_uom" in vals:
                    line_vals["product_uom"] = service.product_uom.id
                if "display_name" in vals:
                    line_vals["name"] = service.display_name
            if line_vals:
                line.write(line_vals)
