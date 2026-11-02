# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    """Give existing orders a stage.

    stage_id is first computed when its column is created, before the stages
    in data/ exist, so every existing order comes out without one.
    """
    repairs = env["repair.order"].search([])
    env.add_to_compute(repairs._fields["stage_id"], repairs)
    repairs.flush_recordset(["stage_id"])
