odoo.define('ooto_onboarding.systray.ActivityMenu', function (require) {
    "use strict";

    var ActivityMenu = require('mail.systray.ActivityMenu');
    var fieldUtils = require('web.field_utils');
    var rpc = require('web.rpc');

    ActivityMenu.include({
        events: _.extend({}, ActivityMenu.prototype.events, {
            'click .o_task_filter': '_onTaskFilterClick',
            'click .o_reminder_close': '_onReminderCloseClick'
        }),

        _onActivityFilterClick: function (ev) {
            var $el = $(ev.currentTarget);
            var data = _.extend({}, $el.data());
            if (data.res_model === "hr.onboarding.task" && data.filter === "my") {
                this.do_action('ooto_onboarding.ooto_activity_task_action', {
                    additional_context: {
                        search_default_my_tasks: 1
                    }
                });
            } else {
                this._super.apply(this, arguments);
            }
        },

        _onTaskFilterClick: function (ev) {
            ev.stopPropagation();
            var $el = $(ev.currentTarget);
            var data = _.extend({}, $el.data());
            if (data.res_model === "hr.onboarding.task") {
                this.do_action({
                    type: 'ir.actions.act_window',
                    name: data.model_name,
                    res_model: data.res_model,
                    res_id: data.res_id,
                    views: [[false, 'form'], [false, 'kanban'], [false, 'list']],
                });
            }
        },

        _onReminderCloseClick: function (ev) {
            ev.stopPropagation();
            var self = this;
            var $el = $(ev.currentTarget);
            var data = _.extend({}, $el.data());
            rpc.query({
                model: 'task.reminder.notif',
                method: 'done_reminder_notif',
                args: [data['res_id']]
            }, {async: false}).then(function (res) {
                self._updateActivityPreview();
            });
        }
    });

});
