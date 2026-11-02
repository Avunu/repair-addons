// Copyright 2026 Avunu LLC (avu.nu)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import { registry } from "@web/core/registry";

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
            content: "Skipping a step: refused with a message",
            trigger: `${column("New")} ${card("Stage Tour Beta")}`,
            run: `drag_and_drop (${column("Under Repair")})`,
        },
        {
            trigger: ".modal:contains('one step forward') .modal-footer .btn-primary",
            run: "click",
        },
        {
            trigger: `body:not(:has(.modal)) ${column("New")} ${card("Stage Tour Beta")}`,
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
