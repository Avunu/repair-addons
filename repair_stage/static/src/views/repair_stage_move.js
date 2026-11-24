// Copyright 2026 Avunu LLC (avu.nu)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

/**
 * Move a repair order to a stage the way its buttons would, opening whatever
 * confirmation dialog a step needs (Confirm, Finalize).
 *
 * A move across several statuses runs one step at a time, and a step may open
 * a dialog. Once a dialog is completed, keep going until the order reaches the
 * target stage. Stop when a round changed nothing (dialog dismissed).
 *
 * @param {Object} env - needs `orm` and `action`
 * @param {Object} params
 * @param {String} params.resModel
 * @param {Number} params.resId
 * @param {Number} params.stageId - the stage to reach
 * @param {Object} [params.context]
 */
export async function moveToStage({orm, action}, {resModel, resId, stageId, context}) {
    const read = async () =>
        (await orm.read(resModel, [resId], ["state", "stage_id"]))[0];
    for (let round = 0; round < 6; round++) {
        const before = await read();
        await new Promise((resolve, reject) => {
            // OnClose also runs straight away when the step needs no dialog.
            action
                .doActionButton({
                    type: "object",
                    name: "action_set_stage",
                    resModel,
                    resId,
                    args: JSON.stringify([stageId]),
                    context,
                    onClose: resolve,
                })
                .catch(reject);
        });
        const after = await read();
        if (after.stage_id[0] === stageId || after.state === before.state) {
            break;
        }
    }
}
