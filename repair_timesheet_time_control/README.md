# Repair Timesheet Time Control

Glue between OCA's `repair_timesheet` (which links timesheet lines to a repair order) and `project_timesheet_time_control` (which provides the start/stop timer). Neither knows about the other: the timer ships wired to projects and tasks only, and the repair order's Timesheets tab is manual entry. This module puts **Start Timer / Stop Timer** on the repair order itself.

## What it adds

-   **Timer on the repair order** — `repair.order` inherits `hr.timesheet.time_control.mixin` and points it at `account.analytic.line.repair_order_id`. The header buttons flip between Start and Stop, and the resulting hours land in the Timesheets tab and its Total Hours rollup.
-   **One-tap start** — the timer wizard opens with the description prefilled (repair order plus vehicle, when `repair_fleet_vehicle` is installed) and the project taken from the company setting below. Picking a job back up later reuses the technician's own last line on that repair order, so the second stint carries the first one's description and project.
-   **Per-line controls** in the Timesheets tab — resume an earlier stint or stop the running one without leaving the repair order.
-   **Repair Labor Project** setting (Settings ▸ Timesheets ▸ Repair Orders, stored on the company as `repair_timesheet_project_id`).

## Why the project is mandatory

A timesheet is an analytic line *with a project*: `hr_timesheet` skips anything else on create ("it is not a timesheet"), and the time control only recognises a running line when its project has **Allow Timesheets**. So a repair order timer still writes to a project — the setting exists so no technician ever has to pick one. [`shop_demo`](https://github.com/Avunu/vertical-auto-repair-addons/tree/develop/shop_demo) (in vertical-auto-repair-addons) seeds a **Shop Labor** project and points the setting at it.

## The timer belongs to whoever is logged in

This is inherited behaviour, not a choice this module makes, and it decides how the shop uses tablets:

-   Running lines are matched with `user_id = <current user>`, so **Start/Stop state is per user**. On a shared login two technicians share one timer; on their own logins they each get their own.
-   One running timer per employee, shop-wide: starting a second one **stops the first** (that is what the "switch" wizard does), and the wizard refuses to guess if it somehow finds two.
-   `hr_timesheet`'s record rule limits a plain user to their own lines, and the line's employee — hence the hourly cost — is resolved from the logged-in user.
-   Consequently a manager **cannot** stop a technician's timer from the repair order: `button_end_work` looks for a running line belonging to the current user and otherwise raises. Managers correct time by editing the line, which needs *User: all timesheets*.

So every technician needs an internal user with a linked `hr.employee`. Portal users cannot log time.

## Requirements

`repair_timesheet` and `base_repair_config` from [OCA/repair](https://github.com/OCA/repair), and `project_timesheet_time_control` from [OCA/project](https://github.com/OCA/project). With `hr_timesheet_begin_end` and `hr_timesheet_time_control_begin_end` (both in [OCA/timesheet](https://github.com/OCA/timesheet)) also installed, stopped timers additionally display real clock-in/clock-out hours derived from the timer.
