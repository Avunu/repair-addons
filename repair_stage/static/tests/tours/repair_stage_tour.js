// Copyright 2026 Avunu LLC (avu.nu)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import {registry} from "@web/core/registry";

const column = (title) => `.o_kanban_group:has(.o_column_title:contains('${title}'))`;
const card = (name) => `.o_kanban_record:contains('${name}')`;

registry.category("web_tour.tours").add("repair_stage_board", {
    url: "/odoo/action-repair.action_repair_order_tree?view_type=kanban",
    steps: () => [
        {
            content: "Same status: only the stage changes",
            trigger: `${column("Confirmed")} ${card("Stage Tour Alpha")}`,
            run: `drag_and_drop (${column("Waiting for Parts")})`,
        },
        {
            trigger: `${column("Waiting for Parts")} ${card("Stage Tour Alpha")}`,
        },
        {
            content: "Into Under Repair: runs Start Repair",
            trigger: `${column("Waiting for Parts")} ${card("Stage Tour Alpha")}`,
            run: `drag_and_drop (${column("Under Repair")})`,
        },
        {
            trigger: `${column("Under Repair")} ${card("Stage Tour Alpha")}`,
        },
        {
            content: "Back to an earlier stage: allowed, status unchanged",
            trigger: `${column("Under Repair")} ${card("Stage Tour Alpha")}`,
            run: `drag_and_drop (${column("Waiting for Parts")})`,
        },
        {
            trigger: `${column("Waiting for Parts")} ${card("Stage Tour Alpha")}`,
        },
        {
            content:
                "Skipping a step: runs the steps in turn, the first opens a dialog",
            trigger: `${column("New")} ${card("Stage Tour Beta")}`,
            run: `drag_and_drop (${column("Under Repair")})`,
        },
        {
            trigger: ".modal:has(.o_form_view) .modal-header .btn-close",
            run: "click",
        },
        {
            trigger: `body:not(:has(.modal)) ${column("New")} ${card("Stage Tour Beta")}`,
        },
        {
            // Closing the dialog ends the move; the board then re-reads the
            // card and reloads. Let that settle so the next drop isn't lost
            // to the reload.
            content: "Wait for the board to reload",
            trigger: `${column("New")} ${card("Stage Tour Beta")}`,
            run: () => new Promise((resolve) => setTimeout(resolve, 1000)),
        },
        {
            content: "A step that needs a dialog opens it",
            trigger: `${column("New")} ${card("Stage Tour Beta")}`,
            run: `drag_and_drop (${column("Waiting for Customer")})`,
        },
        {
            trigger: ".modal:has(.o_form_view) .modal-header .btn-close",
            run: "click",
        },
        {
            trigger: `body:not(:has(.modal)) ${column("New")} ${card("Stage Tour Beta")}`,
        },
    ],
});

registry.category("web_tour.tours").add("repair_stage_form", {
    url: "/odoo/action-repair.action_repair_order_tree",
    steps: () => [
        {
            content: "Open the repair order",
            trigger: ".o_data_row:contains('Stage Form Gamma') .o_data_cell",
            run: "click",
        },
        {
            content: "The form opens with the stage bar",
            trigger: ".o_form_view .o_statusbar_status button:contains('Under Repair')",
        },
        {
            content: "Edit a field without saving",
            trigger: ".o_form_view [name='under_warranty'] input",
            run: "click",
        },
        {
            content: "Pick a stage of a later status: save asks for the dialog",
            trigger: ".o_statusbar_status button:contains('Under Repair')",
            run: "click",
        },
        {
            trigger: ".modal:has(.o_form_view) .modal-header .btn-close",
            run: "click",
        },
        {
            content: "The edit was saved, the stage is unchanged",
            trigger:
                ".o_form_view:not(:has(.modal)) .o_statusbar_status button.o_arrow_button_current:contains('New')",
        },
    ],
});
