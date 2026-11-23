# Repair Stages

Configurable kanban stages for repair orders, the same way Project, CRM and Maintenance
have stages. Each stage belongs to one core repair status (`state`); several stages can
share a status. The core workflow keeps running off `state` alone, so stock
reservations, parts availability and the Confirm / Start / End buttons behave exactly as
before.

- Repairs → Configuration → Stages: add, rename, reorder and fold stages. Ships with
  New, Confirmed, Waiting for Customer, Waiting for Parts, Under Repair, Repaired and
  Cancelled (folded).
- The repairs board is grouped by stage. Managers (Inventory Administrator) can drag
  columns to reorder them.
- Cards can be dropped on any column, in any direction. Moving to a later status runs
  each step in turn, exactly as the buttons would (New → Under Repair confirms, then
  starts); only the last step shows its dialog, so New → Repaired goes straight to
  Finalize without asking to confirm first. Steps that open a dialog (Confirm, Finalize)
  open it on the board, and once it's completed the card carries on to the dropped
  column; dismissing it stops the move there. Moving to Cancelled runs Cancel; leaving
  Cancelled runs Reset to Draft first.
- An open order moved back to a stage of an earlier status, e.g. Under Repair → Waiting
  for Parts, only changes its stage: its status stays and its next step works as usual.
- A Repaired order has no button to reopen it, so moving it elsewhere just sets its
  status back; stock moves already done are left as they are.
- When a button changes the status, the order moves to the first stage (left-most
  column) of the new status.
- Every status must keep at least one active stage.

## Automations

`stage_id` is named so that Automation Rules offer the built-in **Stage is set to**
trigger. A rule fires however the stage changed: a drag on the board, a click on the
status bar, or a button changing the status.

Example: _Stage is set to Waiting for Parts_ → _Create Activity_ "Order parts" for the
parts person.

## Limits

A stage doesn't change core behaviour. To stock and parts logic, "Waiting for Parts" is
still "Confirmed". The form's status bar saves with a plain write, which can't open a
dialog, so it refuses moves that need one; drag the card on the board or use the button
instead.

Depends on `repair`.
