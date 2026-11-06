# Repair Fleet Vehicle

Links repair orders to customer vehicles for a mechanic / repair-shop workflow on Odoo
18 Community.

## What it does

- **`repair.order`** gets a `vehicle_id` (`fleet.vehicle`), filtered to the customer's
  vehicles via `fleet_vehicle_ownership` (`owner_id`) or core `driver_id`, with an "Any
  Owner" toggle to search all vehicles. Picking a vehicle on an empty order fills the
  customer from the owner.
- **Odometer capture**: `odometer_in` is logged to the vehicle's odometer history
  (`fleet.vehicle.odometer`) when the repair is confirmed (skipped if it matches the
  current reading, so re-confirming doesn't duplicate).
- **Customer concern**: an HTML notebook page on the repair order for the issue as
  reported at intake.
- **Search**: stored related `vehicle_license_plate` / `vehicle_vin` enable lookup of
  repair orders by plate or VIN from the search bar.
- **Unit number**: `unit_number` on the vehicle for fleet customers who identify their
  vehicles by their own number. It's on the vehicle form (above the VIN), in the list,
  and searchable.
- **Vehicle history**: a "Repairs" smart button on the vehicle form shows all repair
  orders for that vehicle.
- **Propagation**: the vehicle is copied to the sale order created from the repair order
  ("Create Quotation") and to invoices generated from that sale order, and printed on
  the repair order, quotation, and invoice reports.

## Intake flow

1.  Customer calls or walks in → create a draft Repair Order.
2.  Look up the vehicle by plate (or create it, owner pre-set from customer).
3.  Record the concern in the Customer Concern tab and the odometer reading.
4.  Set the Scheduled Date for the inspection appointment.
