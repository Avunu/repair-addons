# Repair Order Template Services

Extends OCA `repair_order_template` so templates can carry **service lines**
(from OCA `repair_service`) in addition to spare parts.

With this, a "Diagnostic" template can pre-fill the Diagnostic Fee service on
intake, and job templates ("Brake job — tandem axle") can carry book-time
labor lines alongside their parts.

Behavior mirrors the parts lines of the base module: applying a template on a
draft repair order **replaces** the existing service lines when the template
defines any (and leaves them untouched when it doesn't). Auto-installs when
both `repair_order_template` and `repair_service` are installed.
