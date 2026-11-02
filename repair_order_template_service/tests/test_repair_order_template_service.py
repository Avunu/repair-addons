# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepairOrderTemplateService(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Acme Trucking"})
        cls.diag_fee = cls.env["product.product"].create(
            {
                "name": "Diagnostic Fee",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 125.0,
            }
        )
        cls.template = cls.env["repair.order.template"].create(
            {
                "name": "Diagnostic",
                "service_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.diag_fee.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ],
            }
        )

    def test_template_fills_service_lines(self):
        with Form(self.env["repair.order"]) as repair_form:
            repair_form.partner_id = self.partner
            repair_form.repair_order_template_id = self.template
        repair = repair_form.save()
        self.assertEqual(len(repair.repair_service_ids), 1)
        service = repair.repair_service_ids
        self.assertEqual(service.product_id, self.diag_fee)
        self.assertEqual(service.product_uom_qty, 1.0)

    def test_template_replaces_service_lines(self):
        other_service = self.env["product.product"].create(
            {"name": "Shop Labor", "type": "service", "list_price": 150.0}
        )
        with Form(self.env["repair.order"]) as repair_form:
            repair_form.partner_id = self.partner
            with repair_form.repair_service_ids.new() as line:
                line.product_id = other_service
            repair_form.repair_order_template_id = self.template
        repair = repair_form.save()
        self.assertEqual(repair.repair_service_ids.product_id, self.diag_fee)

    def test_template_without_services_keeps_lines(self):
        empty_template = self.env["repair.order.template"].create(
            {"name": "No services"}
        )
        other_service = self.env["product.product"].create(
            {"name": "Shop Labor", "type": "service", "list_price": 150.0}
        )
        with Form(self.env["repair.order"]) as repair_form:
            repair_form.partner_id = self.partner
            with repair_form.repair_service_ids.new() as line:
                line.product_id = other_service
            repair_form.repair_order_template_id = empty_template
        repair = repair_form.save()
        self.assertEqual(repair.repair_service_ids.product_id, other_service)
