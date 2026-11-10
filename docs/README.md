---
title: "Avunu repair addons"
description:
  "Odoo 18.0 modules for the Repairs app: configurable stages, customer vehicles from
  Fleet, service lines on templates and quotations, a work timer on the repair order,
  and parts taken from purchase orders."
---

Odoo 18.0 modules for the Repairs app: configurable stages, customer vehicles from
Fleet, service lines on templates and quotations, a work timer on the repair order, and
parts taken from purchase orders. They are built and maintained by
[Avunu LLC](https://avunu.net) and published for anyone to use. They extend Odoo's core
`repair` module and the modules in [OCA/repair](https://github.com/OCA/repair).

## Modules

### Workflow and vehicles

| Module                                                      | What it does                                                                                                                                                                                                                                                                                            | Licence           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| [`repair_stage`](repair_stage.md)                           | Configurable kanban stages for repair orders, each tied to a core repair status, with drag-and-drop that runs the real status change (Confirm, Start Repair, End Repair); an open order can also be moved back to an earlier stage                                                                      | AGPL-3.0-or-later |
| [`repair_fleet_vehicle`](repair_fleet_vehicle.md)           | Links a repair order to the customer's vehicle in Fleet: odometer reading logged to the vehicle's history on confirmation, a customer concern page, search by plate or VIN, a Repairs button on each vehicle, and the vehicle carried onto the quotation and invoice and printed on all three documents | AGPL-3.0-or-later |
| [`repair_customer_reference`](repair_customer_reference.md) | Adds the sale order's Customer Reference (the customer's PO number) to the repair order, and copies it to the quotation created from the repair; a reference already on the quotation is never replaced                                                                                                 | AGPL-3.0-or-later |

Installing `repair_fleet_vehicle` widens Fleet officers' access. Core Fleet limits them
to the vehicles they drive, which suits company cars but not a shop's customer vehicles,
so the module adds rules that let officers reach every vehicle, odometer reading and
service log; their access rights and the multi-company rules still apply.

### Services and time

OCA `repair_service` adds service lines to repair orders so they can be added to the
sale order, and OCA `repair_timesheet` links timesheet lines to a repair order. These
modules build on them.

| Module                                                              | What it does                                                                                                                                                                                                                           | Licence           |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| [`repair_order_template_service`](repair_order_template_service.md) | Lets OCA `repair_order_template` templates carry service lines as well as parts, so a template can pre-fill a diagnostic fee or book-time labour; installs itself when `repair_order_template` and `repair_service` are both installed | AGPL-3.0-or-later |
| [`repair_service_so_sync`](repair_service_so_sync.md)               | Keeps service lines in step with the sale order after Create Quotation, as core Odoo does for parts: new services add a line, changes update it, and deleting one zeroes its line's quantity; installs itself with `repair_service`    | AGPL-3.0-or-later |
| [`repair_timesheet_time_control`](repair_timesheet_time_control.md) | Starts and stops the work timer from the repair order itself, logging to its Timesheets tab against a project set once per company; joins `repair_timesheet` to the timer from OCA `project_timesheet_time_control`                    | AGPL-3.0-or-later |

### Parts

| Module                                                          | What it does                                                                                                                                                                                                                                                                                                                   | Licence           |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------- |
| [`repair_purchase_order_parts`](repair_purchase_order_parts.md) | Adds every part on a purchase order to an existing repair order in one click, from the repair order or from the purchase order or its receipt, so a repair order can be built before its parts are on hand; links the two through Odoo's own Purchases and Repair Orders smart buttons, however the purchase order was created | AGPL-3.0-or-later |

## Branches

`develop` is the default branch and where pull requests go. Its code targets Odoo 18.0,
the series named in `.odoo-series`. `18.0` follows `develop` automatically (a workflow
fast-forwards it after every push) and is the branch to install or pin. When a newer
Odoo series is maintained, it gets its own branch (`19.0`, …) and changes flow up to it
from `develop`.

## Install

Requires Odoo 18.0 and a PostgreSQL database. Pick the module or modules you want; each
pulls in the modules it depends on (see below), and those must be on your `addons_path`
first.

With a plain Odoo checkout, clone this repository on its `18.0` branch and add it to the
addons path:

```sh
git clone --branch 18.0 https://github.com/Avunu/repair-addons.git
odoo-bin --addons-path=odoo/addons,/path/to/repair-addons,<your other addons paths> \
  -d <database> -i <module> --stop-after-init
```

With [odoo-nix](https://github.com/Avunu/odoo-nix), add the repository from the dev
shell. `odoo module add` accepts an `owner/repo` and a branch, adds it as a submodule,
and the addons path is regenerated from the folders present (run `direnv reload`
afterwards):

```sh
odoo module add Avunu/repair-addons 18.0
```

Add the OCA repositories your modules need the same way, for example
`odoo module add OCA/repair 18.0`.

## Dependencies

Each module's `__manifest__.py` is the source of truth. Besides Odoo core modules
(`repair`, `purchase`, `purchase_repair`), the modules depend on the following. The OCA
repositories listed are the 18.0 branches; clone the ones your chosen modules need.

| Module                          | Needs from OCA or others                                                                                                                                                    | Python packages |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| `repair_stage`                  | none beyond core                                                                                                                                                            | none            |
| `repair_fleet_vehicle`          | `fleet_vehicle_ownership` ([OCA/fleet](https://github.com/OCA/fleet))                                                                                                       | none            |
| `repair_customer_reference`     | none beyond core                                                                                                                                                            | none            |
| `repair_order_template_service` | `repair_order_template` and `repair_service` ([OCA/repair](https://github.com/OCA/repair))                                                                                  | none            |
| `repair_service_so_sync`        | `repair_service` ([OCA/repair](https://github.com/OCA/repair))                                                                                                              | none            |
| `repair_timesheet_time_control` | `repair_timesheet` and `base_repair_config` ([OCA/repair](https://github.com/OCA/repair)), `project_timesheet_time_control` ([OCA/project](https://github.com/OCA/project)) | none            |
| `repair_purchase_order_parts`   | none beyond core                                                                                                                                                            | none            |

`repair_timesheet_time_control` also works with modules it does not require: with
`hr_timesheet_begin_end` and `hr_timesheet_time_control_begin_end`
([OCA/timesheet](https://github.com/OCA/timesheet)) installed, stopped timers show
clock-in and clock-out hours, and with `repair_fleet_vehicle` installed, the timer's
prefilled description names the vehicle.

## Development

The repository carries its own development environment, built by
[odoo-nix](https://github.com/Avunu/odoo-nix) in addons mode. OCB and the repositories
these modules depend on are flake inputs pinned in `flake.lock`, and the Python
environment is locked in `nix/`. You need Nix with flakes, and optionally direnv.

```sh
git clone https://github.com/Avunu/repair-addons.git && cd repair-addons
direnv allow                  # or: nix develop --no-pure-eval
devenv up                     # PostgreSQL, Odoo and Mailpit
odoo db provision             # a database with every module here installed
odoo test repair_fleet_vehicle
```

After `nix flake update`, or when a module gains a `depends` or a Python requirement,
run `odoo project relock` and commit `flake.lock` and `nix/`. A new dependency on
another repository also needs its input and an `externalSources` entry in `flake.nix`.
See odoo-nix's
[A repository of addons](https://github.com/Avunu/odoo-nix/blob/main/docs/scaffolding/addons-repository.md).

## Tests

Odoo runs a module's tests when you install or update it with `--test-enable`. Select a
module's tests with a `--test-tags` filter and use a throwaway database:

```sh
odoo-bin -c odoo.conf -d <testdb> -i <module> \
  --test-enable --test-tags /<module> --stop-after-init
```

Every module has automated tests. `repair_stage` also includes a browser tour of the
repairs board (dragging cards between stages) that runs after install; Odoo skips it
when it cannot find a Chrome or Chromium browser.

## Licence

Every module is licensed under the
[GNU Affero General Public License v3.0 or later](https://github.com/Avunu/repair-addons/blob/18.0/LICENSE).
The licence of each module is also stated in its `__manifest__.py` (`AGPL-3`, Odoo's
identifier for version 3). No module vendors third-party code.

## Provenance

These modules were first developed in a private Avunu project and imported here.
