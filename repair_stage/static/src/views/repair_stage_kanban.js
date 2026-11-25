// Copyright 2026 Avunu LLC (avu.nu)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import {RelationalModel} from "@web/model/relational_model/relational_model";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {moveToStage} from "./repair_stage_move";
import {registry} from "@web/core/registry";

/**
 * Dropping a repair card on another stage column runs the status change that
 * stage implies, the same as pressing the button on the order. Same pattern
 * as crm's CrmKanbanDynamicGroupList.
 *
 * The stock move would just write `stage_id`, and a plain write can't open a
 * dialog - but Confirm and End Repair open one (repair_service_workflow's
 * wizards). So cross-column drops call `action_set_stage` the way a button
 * on the card would (doActionButton), which opens whatever dialog the step
 * returns. The board is reloaded afterwards rather than moving the card
 * optimistically: the server may refuse the move or put the card elsewhere.
 */
export class RepairStageKanbanDynamicGroupList extends RelationalModel.DynamicGroupList {
    async moveRecord(dataRecordId, dataGroupId, refId, targetGroupId) {
        if (dataGroupId === targetGroupId || this.groupByField.name !== "stage_id") {
            return super.moveRecord(...arguments);
        }
        const sourceGroup = this.groups.find((g) => g.id === dataGroupId);
        const targetGroup = this.groups.find((g) => g.id === targetGroupId);
        const record = sourceGroup.list.records.find((r) => r.id === dataRecordId);
        try {
            await moveToStage(this.model, {
                resModel: this.resModel,
                resId: record.resId,
                stageId: targetGroup.value,
                context: this.context,
            });
        } finally {
            await this.model.load();
        }
    }
}

export class RepairStageKanbanModel extends RelationalModel {
    static DynamicGroupList = RepairStageKanbanDynamicGroupList;
}

export const repairStageKanbanView = {
    ...kanbanView,
    Model: RepairStageKanbanModel,
};

registry.category("views").add("repair_stage_kanban", repairStageKanbanView);
