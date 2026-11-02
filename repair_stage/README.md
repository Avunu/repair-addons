# Repair Stages

Configurable kanban stages for repair orders, the same way Project, CRM and
Maintenance have stages. Each stage belongs to one core repair status
(`state`); several stages can share a status. The core workflow keeps
running off `state` alone, so stock reservations, parts availability and the
Confirm / Start / End buttons behave exactly as before.

- Repairs → Configuration → Stages: add, rename, reorder and fold stages.
  Ships with New, Confirmed, Waiting for Customer, Waiting for Parts,
  Under Repair, Repaired and Cancelled (folded).
- The repairs board is grouped by stage. Managers (Inventory Administrator)
  can drag columns to reorder them.
- Dropping a card on a column of a later status runs that step, exactly as
  the button would: New → Confirmed runs Confirm (opening its dialog when
  there is one), Confirmed → Under Repair runs Start Repair, Under Repair →
  Repaired runs End Repair. Skipping a step or cancelling is refused; use
  the buttons on the order.
- An open order can be moved back to any stage of an earlier status, e.g.
  Under Repair → Waiting for Parts when a part turns out to be missing. That
  only changes its stage: it stays Under Repair, and its next step (End
  Repair) works as usual. Repaired and cancelled orders can't be moved back.
- When a button changes the status, the order moves to the first stage
  (left-most column) of the new status.
- Every status must keep at least one active stage.

## Automations

`stage_id` is named so that Automation Rules offer the built-in
**Stage is set to** trigger. A rule fires however the stage changed: a drag
on the board, a click on the status bar, or a button changing the status.

Example: *Stage is set to Waiting for Parts* → *Create Activity* "Order
parts" for the parts person.

## Limits

A stage doesn't change core behaviour. To stock and parts logic, "Waiting
for Parts" is still "Confirmed". The form's status bar saves with a plain
write, which can't open a dialog, so it refuses moves that need one; drag
the card on the board or use the button instead.

Depends on `repair`.
