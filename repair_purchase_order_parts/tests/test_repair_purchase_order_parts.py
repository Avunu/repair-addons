# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepairPurchaseOrderParts(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.customer = cls.env["res.partner"].create({"name": "Repair Customer"})
        cls.vendor = cls.env["res.partner"].create({"name": "NAPA Vendor"})
        cls.item_to_repair = cls.env["product.product"].create(
            {"name": "Widget", "type": "consu", "is_storable": True}
        )
        cls.part_a = cls.env["product.product"].create(
            {"name": "Brake Pad", "type": "consu", "is_storable": True}
        )
        cls.part_b = cls.env["product.product"].create(
            {"name": "Brake Rotor", "type": "consu", "is_storable": True}
        )
        cls.repair = cls.env["repair.order"].create(
            {
                "product_id": cls.item_to_repair.id,
                "product_uom": cls.unit.id,
                "partner_id": cls.customer.id,
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.part_a.id,
                            "name": cls.part_a.name,
                            "product_qty": 2.0,
                            "product_uom": cls.unit.id,
                            "price_unit": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.part_b.id,
                            "name": cls.part_b.name,
                            "product_qty": 1.0,
                            "product_uom": cls.unit.id,
                            "price_unit": 40.0,
                        },
                    ),
                ],
            }
        )
        cls.part_c = cls.env["product.product"].create(
            {"name": "Brake Caliper", "type": "consu", "is_storable": True}
        )
        cls.purchase_order_2 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.part_c.id,
                            "name": cls.part_c.name,
                            "product_qty": 1.0,
                            "product_uom": cls.unit.id,
                            "price_unit": 60.0,
                        },
                    ),
                ],
            }
        )

    def test_select_adds_every_line_as_a_part(self):
        self.purchase_order.with_context(
            repair_id=self.repair.id
        ).action_select_for_repair()

        parts = self.repair.move_ids.filtered(lambda m: m.repair_line_type == "add")
        self.assertEqual(set(parts.product_id.ids), {self.part_a.id, self.part_b.id})
        rotor_move = parts.filtered(lambda m: m.product_id == self.part_b)
        self.assertEqual(rotor_move.product_uom_qty, 1.0)
        self.assertEqual(
            rotor_move.created_purchase_line_ids,
            self.purchase_order.order_line.filtered(
                lambda line: line.product_id == self.part_b
            ),
        )

    def test_selecting_the_same_order_twice_does_not_duplicate_parts(self):
        self.purchase_order.with_context(
            repair_id=self.repair.id
        ).action_select_for_repair()
        with self.assertRaises(UserError):
            self.purchase_order.with_context(
                repair_id=self.repair.id
            ).action_select_for_repair()
        parts = self.repair.move_ids.filtered(lambda m: m.repair_line_type == "add")
        self.assertEqual(len(parts), 2)

    def test_picker_blocked_on_done_or_cancelled_repair(self):
        self.repair.state = "cancel"
        with self.assertRaises(UserError):
            self.repair.action_add_parts_from_purchase_order()

    def test_add_selected_adds_lines_from_every_checked_order(self):
        orders = self.purchase_order + self.purchase_order_2
        orders.with_context(repair_id=self.repair.id).action_add_selected_to_repair()

        parts = self.repair.move_ids.filtered(lambda m: m.repair_line_type == "add")
        self.assertEqual(
            set(parts.product_id.ids),
            {self.part_a.id, self.part_b.id, self.part_c.id},
        )

    def test_add_selected_skips_already_linked_orders_in_the_batch(self):
        self.purchase_order.with_context(
            repair_id=self.repair.id
        ).action_select_for_repair()

        orders = self.purchase_order + self.purchase_order_2
        orders.with_context(repair_id=self.repair.id).action_add_selected_to_repair()

        parts = self.repair.move_ids.filtered(lambda m: m.repair_line_type == "add")
        self.assertEqual(
            set(parts.product_id.ids),
            {self.part_a.id, self.part_b.id, self.part_c.id},
        )
        # part_a/part_b weren't duplicated by being re-selected alongside
        # the genuinely new purchase_order_2
        self.assertEqual(len(parts), 3)

    def test_add_selected_raises_when_every_order_is_already_linked(self):
        orders = self.purchase_order + self.purchase_order_2
        orders.with_context(repair_id=self.repair.id).action_add_selected_to_repair()
        with self.assertRaises(UserError):
            orders.with_context(
                repair_id=self.repair.id
            ).action_add_selected_to_repair()

    def test_smart_buttons_connect_both_documents(self):
        self.purchase_order.with_context(
            repair_id=self.repair.id
        ).action_select_for_repair()
        self.assertEqual(self.repair.purchase_count, 1)
        self.assertIn(self.purchase_order, self.repair._get_linked_purchase_orders())
        self.assertEqual(self.purchase_order.repair_count, 1)
        self.assertIn(self.repair, self.purchase_order._get_linked_repair_orders())
