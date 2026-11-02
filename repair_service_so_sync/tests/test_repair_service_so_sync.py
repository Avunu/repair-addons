# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepairServiceSoSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Acme Trucking"})
        cls.labor = cls.env["product.product"].create(
            {
                "name": "Shop Labor",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 150.0,
            }
        )
        cls.diag_fee = cls.env["product.product"].create(
            {
                "name": "Diagnostic Fee",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 125.0,
            }
        )
        cls.repair = cls.env["repair.order"].create(
            {
                "partner_id": cls.partner.id,
                "repair_service_ids": [
                    (0, 0, {"product_id": cls.diag_fee.id, "product_uom_qty": 1.0})
                ],
            }
        )

    def test_initial_services_get_linked(self):
        self.repair.action_create_sale_order()
        service = self.repair.repair_service_ids
        self.assertTrue(service.sale_line_id)
        self.assertEqual(service.sale_line_id.product_id, self.diag_fee)
        self.assertEqual(service.sale_line_id.price_unit, 125.0)

    def test_service_added_after_quotation_syncs(self):
        self.repair.action_create_sale_order()
        service = self.env["repair.service"].create(
            {
                "repair_id": self.repair.id,
                "product_id": self.labor.id,
                "product_uom_qty": 2.0,
            }
        )
        self.assertTrue(service.sale_line_id)
        self.assertEqual(service.sale_line_id.order_id, self.repair.sale_order_id)
        self.assertEqual(service.sale_line_id.product_uom_qty, 2.0)

    def test_qty_change_updates_sale_line(self):
        self.repair.action_create_sale_order()
        service = self.repair.repair_service_ids
        service.product_uom_qty = 3.0
        self.assertEqual(service.sale_line_id.product_uom_qty, 3.0)

    def test_product_change_updates_sale_line(self):
        self.repair.action_create_sale_order()
        service = self.repair.repair_service_ids
        service.product_id = self.labor
        self.assertEqual(service.sale_line_id.product_id, self.labor)
        self.assertEqual(service.sale_line_id.price_unit, 150.0)

    def test_unlink_zeroes_sale_line(self):
        self.repair.action_create_sale_order()
        service = self.repair.repair_service_ids
        sale_line = service.sale_line_id
        service.unlink()
        self.assertTrue(sale_line.exists())
        self.assertEqual(sale_line.product_uom_qty, 0.0)

    def test_no_sync_without_sale_order(self):
        service = self.env["repair.service"].create(
            {
                "repair_id": self.repair.id,
                "product_id": self.labor.id,
                "product_uom_qty": 1.0,
            }
        )
        self.assertFalse(service.sale_line_id)
