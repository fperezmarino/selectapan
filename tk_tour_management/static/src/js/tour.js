odoo.define('tk_tour_management.TourDashboard', function (require) {
    'use strict';
    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session')
    const web_client = require('web.web_client');
    const _t = core._t;
    const QWeb = core.qweb;

    const ActionMenu = AbstractAction.extend({

        template: 'tourDashboard',

        events: {
            'click .total-booking': 'view_total_booking',
            'click .draft-booking': 'view_draft_booking',
            'click .confirm-booking': 'view_confirm_booking',
            'click .total-inquiry': 'view_total_inquiry',
            'click .package-domestic': 'view_package_domestic',
            'click .package-international': 'view_package_international',
            'click .total-packages': 'view_total_packages',
        },
        renderElement: function (ev) {
            const self = this;
            $.when(this._super())
                .then(function (ev) {
                    rpc.query({
                        model: "tour.booking",
                        method: "get_tour_stats",
                    }).then(function (result) {
                        $('#book_draft').empty().append(result['book_draft']);
                        $('#book_confirm').empty().append(result['book_confirm']);
                        $('#total_booking').empty().append(result['total_booking']);
                        $('#package_lead').empty().append(result['package_lead']);
                        $('#domestic_packages').empty().append(result['domestic_packages']);
                        $('#international_packages').empty().append(result['international_packages']);
                        $('#total_package').empty().append(result['total_package']);
//                        $('#rent_total').empty().append(result['rent_total']);
                    });
                });
        },
        view_total_booking : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Total Booking'),
                type: 'ir.actions.act_window',
                res_model: 'tour.booking',
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_draft_booking : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Draft Booking'),
                type: 'ir.actions.act_window',
                res_model: 'tour.booking',
                domain: [['stage', '=', 'draft']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_confirm_booking : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Confirm Booking'),
                type: 'ir.actions.act_window',
                res_model: 'tour.booking',
                domain: [['stage', '=', 'confirm']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_total_inquiry : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Tour Inquiry'),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_package_domestic : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Domestic Packages'),
                type: 'ir.actions.act_window',
                res_model: 'tour.package',
                domain: [['tour_type', '=', 'domestic']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_package_international : function (ev){
             ev.preventDefault();
            return this.do_action({
                name: _t('International Packages'),
                type: 'ir.actions.act_window',
                res_model: 'tour.package',
                domain: [['tour_type', '=', 'international']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_total_packages : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Packages'),
                type: 'ir.actions.act_window',
                res_model: 'tour.package',
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },

        get_action: function (ev, name, res_model){
            ev.preventDefault();
            return this.do_action({
                name: _t(name),
                type: 'ir.actions.act_window',
                res_model: res_model,
                views: [[false, 'kanban'],[false, 'tree'],[false, 'form']],
                target: 'current'
            });
        },

        willStart: function () {
            const self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('tour_dashboard', ActionMenu);

});
