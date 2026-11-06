# Repair Purchase Order Parts

Lets a repair order be built before its parts are on hand: add a purchase order's lines
to an existing repair order's Parts in one click, once that purchase order exists (e.g.
from a NAPA/EDI PDF import).

## Why

Odoo's built-in repair↔purchase link (`purchase_repair`) only connects a repair order
to a purchase order when Odoo's own procurement engine generates that purchase order
from the repair's demand (via a Buy route + replenishment). A purchase order created
another way - imported from a vendor PDF, for instance - has no such link, and the
repair order's parts still have to be entered by hand.

## What it does

- **Repair order → Parts tab**: next to the existing **Catalog** button, a new
  **Purchase Orders** button opens a list of purchase orders to choose from.
- Clicking a row adds every product line on that purchase order to the repair order as a
  part to add (`repair_line_type = 'add'`), with the quantity and unit of measure from
  the purchase order line.
- Each added part's `created_purchase_line_ids` is set to its source purchase order
  line - the same field Odoo's own replenishment sets - so the repair order's
  **Purchases** smart button and the purchase order's **Repair Orders** smart button
  connect the two documents either way, regardless of how the purchase order was
  created.
- Re-selecting a purchase order already added to a repair order skips lines that are
  already linked, so it can't add the same part twice.

## What it does not do

This only tags parts with where they're being purchased from - it does not reserve
incoming stock to a specific repair order. Once the purchase order is received, ordinary
reservation rules apply: the stock goes to whichever job needing that product is served
first, the same as it would if the part had simply been in stock already.
