# Repair Service Sale Order Sync

OCA `repair_service` pushes service (labor) lines to the sale order only at "Create Quotation" time — services added, changed, or removed on the repair order **afterwards** never reach the customer-facing quotation.

This module keeps them in sync, mirroring the behavior core Odoo implements for spare parts (`stock.move` ↔ `sale.order.line`):

-   each `repair.service` remembers its generated `sale_line_id`;
-   services created while a sale order exists immediately add a line;
-   quantity / product / unit / description changes update the linked line;
-   deleting a service zeroes the linked line's quantity (not deleted, so confirmed orders keep their audit trail).

Auto-installs with `repair_service`.
