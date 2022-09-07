odoo.define('ooto_onboarding.reminder', function (require) {
    'use strict';

    var BasicModel = require('web.BasicModel');
    var field_registry = require('web.field_registry');
    var Notification = require('web.Notification');
    var relational_fields = require('web.relational_fields');
    var session = require('web.session');
    var WebClient = require('web.WebClient')
    var rpc = require('web.rpc');

    var OnboardingTaskNotification = Notification.extend({
        template: "OnboardingTaskNotification",

        init: function (parent, params) {
            this._super(parent, params);
            this.eid = params.eventID;
            this.reminder_id = params.reminderID;
            this.sticky = true;
            this.events = _.extend(this.events || {}, {
                'click .link2task': function () {
                    var self = this;

                    this._rpc({
                        route: '/web/action/load',
                        params: {
                            action_id: 'ooto_onboarding.ooto_activity_open_task_action',
                        },
                    })
                        .then(function (r) {
                            r.res_id = self.eid;
                            return self.do_action(r);
                        });
                },
                'click .link2showed': function () {
                    var self = this;
                    rpc.query({
                        model: 'task.reminder.notif',
                        method: 'mark_as_shown_reminder_notif',
                        args: [self.reminder_id],
                    }, {async: false}).then(function (res) {
                        self.destroy();
                    });
                },

                'click .o_close': function () {
                    var self = this;
                    rpc.query({
                        model: 'task.reminder.notif',
                        method: 'mark_as_shown_reminder_notif',
                        args: [self.reminder_id],
                    }, {async: false}).then(function (res) {
                        self.destroy();
                    });
                }
            });
        },
    });

    WebClient.include({
        display_task_notif: function (notifications) {
            var self = this;
            var last_notif_timer = 0;
            clearTimeout(this.get_next_task_notif_timeout);
            _.each(this.task_notif_timeouts, clearTimeout);
            _.each(this.task_notif, function (notificationID) {
                self.call('notification', 'close', notificationID, true);
            });
            this.task_notif_timeouts = {};
            this.task_notif = {};
            _.each(notifications, function (notif) {
                self.task_notif_timeouts[notif.event_id] = setTimeout(function () {
                    var notificationID = self.call('notification', 'notify', {
                        Notification: OnboardingTaskNotification,
                        title: notif.title,
                        message: notif.message,
                        eventID: notif.event_id,
                        reminderID: notif.reminder_id,
                    });
                    self.task_notif[notif.event_id] = notificationID;
                }, notif.timer * 1000);
                last_notif_timer = Math.max(last_notif_timer, notif.timer);
            });
            if (last_notif_timer > 0) {
                this.get_next_task_notif_timeout = setTimeout(this.get_next_task_notif.bind(this), last_notif_timer * 1000);
            }
        },
        get_next_task_notif: function () {
            session.rpc("/task/notify", {}, {shadow: true})
                .then(this.display_task_notif.bind(this))
                .guardedCatch(function(reason) {
                    var err = reason.message;
                    var ev = reason.event;
                    if(err.code === -32098) {
                        ev.preventDefault();
                    }
                });
        },
        show_application: function () {
            this.task_notif_timeouts = {};
            this.task_notif = {};
            this.call('bus_service', 'onNotification', this, function (notifications) {
                _.each(notifications, (function (notification) {
                    if (notification[0][1] === 'hr.onboarding.task') {
                        this.display_task_notif(notification[1]);
                    }
                }).bind(this));
            });
            return this._super.apply(this, arguments).then(this.get_next_task_notif.bind(this));
        },
    });


});