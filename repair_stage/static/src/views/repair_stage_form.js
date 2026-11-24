// Copyright 2026 Avunu LLC (avu.nu)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import {Record} from "@web/model/relational_model/record";
import {RelationalModel} from "@web/model/relational_model/relational_model";
import {formView} from "@web/views/form/form_view";
import {markRaw} from "@odoo/owl";
import {moveToStage} from "./repair_stage_move";
import {registry} from "@web/core/registry";

/**
 * Saving a repair order whose stage was changed (by the stage bar or by the
 * field) runs the status change that stage implies, the same as dropping the
 * card on the board. A plain write can't open a dialog, but Confirm and End
 * Repair need one, so the form would refuse the save and lose the user's
 * changes.
 *
 * Instead the other changes are saved first (a step may depend on them), then
 * the stage move runs through `action_set_stage`, opening any dialog the step
 * needs. If the save fails, the stage change stays pending with everything
 * else. If the dialog is dismissed, the order keeps its saved changes and
 * its previous stage.
 */
export class RepairStageFormRecord extends Record {
    async _save(options = {}) {
        const target = this.resId && this._changes.stage_id;
        if (!target || !target.id || target.id === this._values.stage_id?.id) {
            return super._save(options);
        }
        const {nextId, ...saveOptions} = options;
        const withStage = this._changes;
        const withoutStage = {...withStage};
        delete withoutStage.stage_id;
        this._changes = markRaw(withoutStage);
        this.data = {...this._values, ...this._changes};
        let saved = false;
        try {
            saved = await super._save({...saveOptions, reload: true});
        } finally {
            if (!saved) {
                // Keep the pending stage change along with the rest of the edits.
                this._changes = markRaw({...this._changes, stage_id: target});
                this.data = {...this._values, ...this._changes};
            }
        }
        if (!saved) {
            return false;
        }
        try {
            await moveToStage(this.model, {
                resModel: this.resModel,
                resId: this.resId,
                stageId: target.id,
                context: this.context,
            });
        } finally {
            await this._load();
        }
        if (nextId) {
            return this.model.load({resId: nextId});
        }
        return true;
    }
}

export class RepairStageFormModel extends RelationalModel {
    static Record = RepairStageFormRecord;
}

export const repairStageFormView = {
    ...formView,
    Model: RepairStageFormModel,
};

registry.category("views").add("repair_stage_form", repairStageFormView);
