# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairOrderTemplate(models.Model):
    _inherit = "repair.order.template"

    service_line_ids = fields.One2many(
        comodel_name="repair.order.template.service.line",
        inverse_name="template_id",
        check_company=True,
    )


class RepairOrderTemplateServiceLine(models.Model):
    _name = "repair.order.template.service.line"
    _description = "Repair Order Template Service Line"
    _check_company_auto = True

    template_id = fields.Many2one(
        "repair.order.template",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        related="template_id.company_id",
        store=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Service",
        domain=[("type", "=", "service")],
        check_company=True,
        required=True,
    )
    name = fields.Text(
        string="Description",
        help="Optional description for the service line; defaults to the "
        "product name.",
    )
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id",
    )
    product_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
        compute="_compute_product_uom",
        readonly=False,
        required=True,
        precompute=True,
        store=True,
    )
    product_uom_qty = fields.Float(
        "Quantity",
        digits="Product Unit of Measure",
        required=True,
        default=1.0,
    )

    @api.depends("product_id")
    def _compute_product_uom(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id

    def _prepare_service_values(self):
        vals = {
            "product_id": self.product_id.id,
            "product_uom": self.product_uom.id,
            "product_uom_qty": self.product_uom_qty,
        }
        if self.name:
            vals["display_name"] = self.name
        return vals
