# Repair Customer Reference

A sale order has a Customer Reference (`client_order_ref`), the customer's own PO
number. This module gives the repair order the same field, so a repair tied to a
customer PO can carry it from the start, and copies it to the quotation created from the
repair.

- **`repair.order`** gets `client_order_ref`, "Customer Reference", defined as on
  `sale.order` (`Char`, not copied on duplicate). It is on the form below Tags, an
  optional column in the list, searchable, and printed on the repair order report.
- **Quotations**: whatever way a sale order is created from a repair order (Create
  Quotation, or `repair_order_group` for several repairs) it starts with the repair's
  reference. An order covering several repairs lists each distinct reference once,
  separated by commas.
- **Added later**: a PO number often arrives after the quotation exists, so setting the
  reference on a repair order also fills the Customer Reference of its sale order if
  that is still empty.

A Customer Reference already set on a sale order is never replaced.
