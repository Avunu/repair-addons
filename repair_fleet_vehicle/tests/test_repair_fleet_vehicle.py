# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged("post_install", "-at_install")
class TestRepairFleetVehicle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Acme Trucking"})
        brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Freightliner"})
        model = cls.env["fleet.vehicle.model"].create(
            {"name": "Cascadia", "brand_id": brand.id}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": model.id,
                "license_plate": "TRK-1234",
                "vin_sn": "1FUJGLDR0LLL12345",
                "owner_id": cls.partner.id,
                "odometer_unit": "miles",
            }
        )

    def _create_repair(self, **extra):
        return self.env["repair.order"].create(
            {
                "partner_id": self.partner.id,
                "vehicle_id": self.vehicle.id,
                **extra,
            }
        )

    def test_onchange_vehicle_sets_partner(self):
        with Form(self.env["repair.order"]) as repair_form:
            repair_form.vehicle_id = self.vehicle
            self.assertEqual(repair_form.partner_id, self.partner)

    def test_related_vehicle_fields(self):
        repair = self._create_repair()
        self.assertEqual(repair.vehicle_license_plate, "TRK-1234")
        self.assertEqual(repair.vehicle_vin, "1FUJGLDR0LLL12345")

    def test_unit_number_printed_on_repair_order(self):
        self.vehicle.unit_number = "T-104"
        repair = self._create_repair()
        html = self.env["ir.actions.report"]._render_qweb_html(
            "repair.action_report_repair_order", repair.ids
        )[0]
        self.assertIn(b"T-104", html)

    def test_odometer_logged_on_confirm(self):
        repair = self._create_repair(odometer_in=120000.0)
        repair.action_validate()
        # odometer is a dependency-less search-based compute; force re-read
        self.vehicle.invalidate_recordset(["odometer"])
        self.assertEqual(self.vehicle.odometer, 120000.0)
        odometer_log = self.env["fleet.vehicle.odometer"].search(
            [("vehicle_id", "=", self.vehicle.id)]
        )
        self.assertEqual(len(odometer_log), 1)
        # Re-confirming with the same reading must not duplicate the log
        repair._log_vehicle_odometer()
        odometer_log = self.env["fleet.vehicle.odometer"].search(
            [("vehicle_id", "=", self.vehicle.id)]
        )
        self.assertEqual(len(odometer_log), 1)

    def test_vehicle_propagates_to_sale_order_and_invoice(self):
        repair = self._create_repair()
        repair.action_create_sale_order()
        sale_order = repair.sale_order_id
        self.assertEqual(sale_order.vehicle_id, self.vehicle)
        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.env["product.product"]
                .create(
                    {
                        "name": "Shop Labor",
                        "type": "service",
                        "invoice_policy": "order",
                        "list_price": 150.0,
                    }
                )
                .id,
                "product_uom_qty": 2.0,
            }
        )
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertEqual(invoice.vehicle_id, self.vehicle)

    def test_vehicle_repair_count(self):
        self._create_repair()
        self._create_repair()
        self.assertEqual(self.vehicle.repair_count, 2)
        action = self.vehicle.action_view_repairs()
        self.assertEqual(action["domain"], [("vehicle_id", "=", self.vehicle.id)])

    def test_officer_reads_a_customer_vehicle(self):
        """Core fleet restricts Officers to vehicles they personally drive.

        Customer vehicles have no staff driver, so without this module's
        record rules an Officer reads none of them and every server-side
        touch of a vehicle raises AccessError.
        """
        # password: password_security is installed and rejects the login-as-
        # password that new_test_user defaults to.
        officer = new_test_user(
            self.env,
            login="fleet_officer",
            password="Fleet-Officer-1!",
            groups="base.group_user,fleet.fleet_group_user",
            company_id=self.env.company.id,
        )
        self.assertFalse(officer.has_group("fleet.fleet_group_manager"))

        vehicle = self.vehicle.with_user(officer)
        self.assertNotEqual(self.vehicle.driver_id, officer.partner_id)
        self.assertTrue(vehicle.display_name)
        self.assertIn(
            self.vehicle, self.env["fleet.vehicle"].with_user(officer).search([])
        )

        # Confirming a repair writes the intake reading to odometer history,
        # which core restricts the same way.
        repair = self._create_repair(odometer_in=99000.0)
        repair.with_user(officer)._log_vehicle_odometer()
        self.assertTrue(
            self.env["fleet.vehicle.odometer"]
            .with_user(officer)
            .search([("vehicle_id", "=", self.vehicle.id)])
        )

    def test_display_name_year_and_unit_only_when_requested(self):
        self.vehicle.write({"model_year": "2016", "unit_number": "T-104"})
        plain = self.vehicle.display_name
        self.assertNotIn("2016", plain)
        self.assertNotIn("T-104", plain)
        labelled = self.vehicle.with_context(show_vehicle_year=True).display_name
        self.assertEqual(labelled, f"2016 {plain} (T-104)")
        # Each part is optional.
        self.vehicle.unit_number = False
        self.assertEqual(
            self.vehicle.with_context(show_vehicle_year=True).display_name,
            f"2016 {plain}",
        )
        self.vehicle.write({"model_year": False, "unit_number": "T-104"})
        self.assertEqual(
            self.vehicle.with_context(show_vehicle_year=True).display_name,
            f"{plain} (T-104)",
        )
        self.vehicle.unit_number = False
        self.assertEqual(
            self.vehicle.with_context(show_vehicle_year=True).display_name, plain
        )

    def test_name_search_matches_unit_number(self):
        self.vehicle.unit_number = "T-104"
        found = self.env["fleet.vehicle"].name_search("T-104")
        self.assertIn(self.vehicle.id, [vehicle_id for vehicle_id, _name in found])
        # Existing matches keep working.
        found = self.env["fleet.vehicle"].name_search("TRK-1234")
        self.assertIn(self.vehicle.id, [vehicle_id for vehicle_id, _name in found])
