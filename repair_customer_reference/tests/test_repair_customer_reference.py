# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepairCustomerReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Acme Trucking"})

    def _repair(self, ref=False, **extra):
        return self.env["repair.order"].create(
            {"partner_id": self.partner.id, "client_order_ref": ref, **extra}
        )

    def test_field_mirrors_sale_order(self):
        repair_field = self.env["repair.order"]._fields["client_order_ref"]
        sale_field = self.env["sale.order"]._fields["client_order_ref"]
        self.assertEqual(repair_field.type, sale_field.type)
        self.assertEqual(repair_field.string, sale_field.string)
        self.assertFalse(repair_field.copy)

    def test_not_copied_on_duplicate(self):
        self.assertFalse(self._repair("PO-1").copy().client_order_ref)

    def test_create_quotation_copies_reference(self):
        repair = self._repair("PO-1001")
        repair.action_create_sale_order()
        self.assertEqual(repair.sale_order_id.client_order_ref, "PO-1001")

    def test_create_quotation_without_reference(self):
        repair = self._repair()
        repair.action_create_sale_order()
        self.assertFalse(repair.sale_order_id.client_order_ref)

    def test_reference_added_later_fills_empty_order(self):
        repair = self._repair()
        repair.action_create_sale_order()
        repair.client_order_ref = "PO-LATE"
        self.assertEqual(repair.sale_order_id.client_order_ref, "PO-LATE")

    def test_existing_order_reference_is_kept(self):
        repair = self._repair("PO-1001")
        repair.action_create_sale_order()
        repair.sale_order_id.client_order_ref = "TYPED-BY-HAND"
        repair.client_order_ref = "PO-CHANGED"
        self.assertEqual(repair.sale_order_id.client_order_ref, "TYPED-BY-HAND")

    def test_order_for_several_repairs_lists_each_reference_once(self):
        repairs = self._repair("PO-A") | self._repair("PO-B") | self._repair("PO-A")
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "repair_order_ids": [(4, repair.id) for repair in repairs],
            }
        )
        self.assertEqual(order.client_order_ref, "PO-A, PO-B")

    def test_linking_repair_to_existing_order_fills_empty_reference(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        order.write({"repair_order_ids": [(4, self._repair("PO-9").id)]})
        self.assertEqual(order.client_order_ref, "PO-9")

    def test_views_and_report(self):
        form = etree.fromstring(self.env["repair.order"].get_view(view_type="form")["arch"])
        self.assertTrue(
            form.xpath(
                "//field[@name='tag_ids']/following-sibling::*[1]"
                "[self::field][@name='client_order_ref']"
            ),
            "Customer Reference sits directly below Tags",
        )
        html = self.env["ir.actions.report"]._render_qweb_html(
            "repair.action_report_repair_order", self._repair("PO-PRINT").ids
        )[0]
        self.assertIn(b"PO-PRINT", html)
