odoo.define("ooto_onboarding.kanban_controller", function(require){
'user strict';
console.log('Kanban controller ready');

var BasicController = require('web.BasicController');
var KanbanController = require('web.KanbanController');

var MyKanbanController = KanbanController.include({
    custom_events: _.extend({}, KanbanController.prototype.custom_events, {
        kanban_record_archive: '_onArchiveRecord',
    }),
    /**
     * @private
     * @param {OdooEvent} event
     */
    _onArchiveRecord: function (event) {
        var self = this;
        var active = event.target.recordData.active;
        var parent = event.target.__parentedParent.db_id;
        var rec = event.target;
        if ([rec.db_id]) {
            this.model
                .toggleActive([rec.db_id], !active, parent)
                .then(function (dbID) {
                    return self.reload(parent);
                });
        }
    },
});
return MyKanbanController;

});