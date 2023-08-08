/** @odoo-module alias=edoob.relational_fields */

import view_registry from 'web.view_registry';
import field_registry from 'web.field_registry';

import { FieldOne2Many } from 'web.relational_fields';
import dialogs from 'web.view_dialogs';
import {_t} from 'web.core'
import Domain from 'web.Domain';
import BasicModel from 'web.BasicModel';
import FormView from 'web.FormView';
import FormController from 'web.FormController';


BasicModel.include({
    _makeDataPoint() {
        const dataPoint = this._super(...arguments)
        dataPoint.getEvalContext = this._getEvalContext.bind(this, dataPoint)
        return dataPoint;
    }
})

const EnrollStudentWizardFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        enroll_wizard_updated: '_onEnrollWizardUpdate'
    }),
    async _onEnrollWizardUpdate() {
        const recordID = this.handle;
        await this.saveRecord(recordID, {stayInEdit: true});
        await this.reload();
    }
})

const EnrollStudentWizardFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: EnrollStudentWizardFormController,
    }),
})

const FieldEnrollFamilyOne2many = FieldOne2Many.extend({
    async _addCreateRecordRow(data) {
        this._openFormDialog({
            context: data.context && data.context[0],
            disable_multiple_selection: data.disable_multiple_selection,
            on_saved: (record) => {
                this._setValue({ operation: 'ADD', id: record.id });
            },
        });
    },

    _onFieldChanged(ev) {
        this._super.apply(this, arguments);
        this.trigger_up('enroll_wizard_updated');
    },

    _onAddExistingRecord(ev){
        const data = ev.data || {};
        ev.stopPropagation();
        this.onAddRecordOpenDialog();
    },

    onAddRecordOpenDialog: function () {
        const domain = this.record.getDomain({fieldName: this.name});
        const context = this.record.getContext(this.recordParams);
        new dialogs.SelectCreateDialog(this, {
            res_model: 'school.family',
            domain: domain.concat(["!", ["id", "in", this.value.res_ids]]),
            context,
            title: _t("Add: ") + this.string,
            no_create: true,
            fields_view: this.attrs.views.form,
            kanban_view_ref: this.attrs.kanban_view_ref,
            disable_multiple_selection: true,
            on_selected: async records => {
                const resIDs = _.pluck(records, 'id');
                context['real_family_id'] = _.first(resIDs);
                this._openFormDialog({
                    context: context,
                    disable_multiple_selection: true,
                    on_saved: (record) => {
                        this._setValue({ operation: 'ADD', id: record.id });
                    },
                });
            }
        }).open();
    },

    _getButtonsRenderingContext() {
        const renderingContext = this._super(...arguments);
        if (this.model === 'enroll.student.form' && this.name === 'family_ids') {
            renderingContext.isEnrollFormFamilyField = true;
        }
        return renderingContext
    },

    _renderButtons() {
        this._super(...arguments);
        if (!this.isReadonly && this.view.arch.tag === 'kanban' && this.$buttons
            && this.model === 'enroll.student.form' && this.name === 'family_ids') {
            this.$buttons.on('click', 'button.o_edoob_add_existing_family', this._onAddExistingRecord.bind(this));
        }
    },
})

const FieldEnrollIndividualToFamilyMany2many = FieldOne2Many.extend({
    init(parent, name, record, options) {
        const res = this._super(...arguments)
        return res;
    },

    async _addCreateRecordRow(data) {
        this._openFormDialog({
            context: this.record.context,
            disable_multiple_selection: data.disable_multiple_selection,
            on_saved: (record) => {
                this._setValue({ operation: 'ADD', id: record.id });
            },
        });
    },
    _onAddExistingRecord(ev){
        const data = ev.data || {};
        ev.stopPropagation();
        if (this._canQuickEdit && this.isReadonly) {
            this.trigger_up('quick_edit', {
                fieldName: this.name,
                target: this.el,
                extraInfo: { type: 'add', data },
            });
        } else {
            this.onAddRecordOpenDialog();
        }
    },

    onAddRecordOpenDialog: function () {
        const realIndividualInFormIds = Array.from(this.record.evalContext.real_individual_in_form_ids).filter(e => !isNaN(e));
        const domain = Domain.prototype.stringToArray([['id', 'not in', realIndividualInFormIds]]);
        const context = this.record.context;
        context['search_default_non_student'] = 1;
        new dialogs.SelectCreateDialog(this, {
            res_model: 'school.family.individual',
            domain,
            context,
            title: _t("Add: ") + this.string,
            no_create: true,
            fields_view: this.attrs.views.form,
            kanban_view_ref: this.attrs.kanban_view_ref,
            on_selected: async records => {
                const resIDs = _.pluck(records, 'id');
                const virtualFamilyIds = await this._rpc({
                    model: 'school.family.individual',
                    method: 'create_enroll_form_individuals',
                    args: [resIDs],
                    context,
                    })
                if (virtualFamilyIds.length) {
                    const values = _.map(virtualFamilyIds, id => ({id}));
                    await this._setValue({
                        operation: 'ADD_M2M',
                        ids: values,
                    });

                    const valueDatas = this.value.data || [];
                    const newValueDatas = valueDatas.filter(vd => virtualFamilyIds.includes(vd.res_id));
                    for (const data of newValueDatas) {
                        this._openFormDialog({
                            id: data.id
                        });
                    }
                }
            }
        }).open();
    },

    onAddRecordInFormOpenDialog: function () {
        const individualInFormIds = Array.from(this.record.evalContext.individual_in_form_ids).filter(e => !isNaN(e));
        const domain = Domain.prototype.stringToArray([['id', 'in', individualInFormIds]]);
        const context = this.record.getContext(this.recordParams);
        context['search_default_non_student'] = 1;
        new dialogs.SelectCreateDialog(this, {
            res_model: 'enroll.student.form.individual',
            domain: domain.concat([["id", "not in", this.value.res_ids]]),
            context,
            title: _t("Add: ") + this.string,
            no_create: true,
            fields_view: this.attrs.views.form,
            kanban_view_ref: this.attrs.kanban_view_ref,
            on_selected: async records => {
                const resIDs = _.pluck(records, 'id');
                const newIDs = _.difference(resIDs, this.value.res_ids);
                if (newIDs.length) {
                    const values = _.map(newIDs, id => ({id}));
                    this._setValue({
                        operation: 'ADD_M2M',
                        ids: values,
                    });
                    const valueDatas = this.value.data || [];
                    const newValueDatas = valueDatas.filter(vd => newIDs.includes(vd.res_id));
                    for (const data of newValueDatas) {
                        this._openFormDialog({
                            id: data.id
                        });
                    }
                }
            }
        }).open();
    },

    _getButtonsRenderingContext() {
        const renderingContext = this._super(...arguments);
        if (this.model === 'enroll.student.form.family' && this.name === 'individual_ids') {
            renderingContext.isEnrollFormIndividualField = true;
        }
        return renderingContext
    },

    _renderButtons() {
        this._super(...arguments);
        if (!this.isReadonly && this.view.arch.tag === 'kanban' && this.$buttons
            && this.model === 'enroll.student.form.family' && this.name === 'individual_ids') {
            this.$buttons.on('click', 'button.o_edoob_add_existing_individual', this._onAddExistingRecord.bind(this));
            this.$buttons.on('click', 'button.o_edoob_add_individual_in_form', this.onAddRecordInFormOpenDialog.bind(this));
        }
    },
})


field_registry.add('enroll_family_one2many', FieldEnrollFamilyOne2many);
field_registry.add('enroll_individual2family_many2many', FieldEnrollIndividualToFamilyMany2many);

view_registry.add('enroll_student_wizard_form_view', EnrollStudentWizardFormView);

return {
    FieldEnrollFamilyOne2many,
    FieldEnrollIndividualToFamilyMany2many,
    EnrollStudentWizardFormView,
    EnrollStudentWizardFormController,
};