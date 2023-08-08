/** @odoo-module alias=school.header.buttons */

import KanbanController from 'web.KanbanController';
import ListController from 'web.ListController';
import FormController from 'web.FormController';

import { ComponentWrapper } from 'web.OwlCompatibility';
const { Component } = owl;

export class SchoolEnrollButton extends Component {
    static template = 'Enroll.button'
    static props = ['btnStyleClass', 'controller']

    goToEnrollWizard() {
        this.props.controller.do_action('edoob.enroll_student_form_action');
    }
}

FormController.include({
    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this._schoolEnrollButton = undefined;
    },

    /**
     * @override
     * @param {jQuery} [$node]
     */
    renderButtons($node) {
        this._super(...arguments);
        if (this.$buttons && this.modelName === 'school.student') {
            this._schoolEnrollButtonTarget = document.createElement('span');
            this.$buttons.find('.o_form_button_create').replaceWith(this._schoolEnrollButtonTarget);
        }
    },

    /**
     * @override
     */
    async start() {
        const res = await this._super(...arguments);
        if (this.modelName === 'school.student' && this.$buttons && this.$buttons.length) {
            this._schoolEnrollButton = new ComponentWrapper(this, SchoolEnrollButton, {btnStyleClass: 'btn-secondary', controller: this});
            await this._schoolEnrollButton.mount(this._schoolEnrollButtonTarget);
        }
        return res
    },
})

ListController.include({
    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this._schoolEnrollButton = undefined;
        this._schoolEnrollButtonTarget = undefined;
    },

    /**
     * @override
     * @param {jQuery} [$node]
     */
    renderButtons($node) {
        this._super(...arguments);
        if (this.$buttons && this.modelName === 'school.student') {
            this._schoolEnrollButtonTarget = document.createElement('span');
            this.$buttons.find('.o_list_button_add').replaceWith(this._schoolEnrollButtonTarget);
        }
    },

    /**
     * @override
     */
    async start() {
        const res = await this._super(...arguments);
        if (this.modelName === 'school.student' && this.$buttons && this.$buttons.length) {
            this._schoolEnrollButton = new ComponentWrapper(this, SchoolEnrollButton, {btnStyleClass: 'btn-primary', controller: this});
            await this._schoolEnrollButton.mount(this._schoolEnrollButtonTarget);
        }
        return res
    },
})

KanbanController.include({
    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this._schoolEnrollButton = undefined;
        this._schoolEnrollButtonTarget = undefined;
    },

    /**
     * @override
     * @param {jQuery} [$node]
     */
    renderButtons($node) {
        this._super(...arguments);
        if (this.$buttons && this.modelName === 'school.student') {
            this._schoolEnrollButtonTarget = document.createElement('span');
            this.$buttons.find('.o-kanban-button-new').replaceWith(this._schoolEnrollButtonTarget);
        }
    },

    /**
     * @override
     */
    async start() {
        const res = await this._super(...arguments);
        if (this.modelName === 'school.student' && this.$buttons && this.$buttons.length) {
            this._schoolEnrollButton = new ComponentWrapper(this, SchoolEnrollButton, {btnStyleClass: 'btn-primary', controller: this});
            await this._schoolEnrollButton.mount(this._schoolEnrollButtonTarget);
        }
        return res
    }
})
