odoo.define("ooto_onboarding.kanban_record", function(require){
'user strict';

var KanbanRecord = require('web.KanbanRecord');

var MyKanbanRecord = KanbanRecord.include({
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onKanbanActionClicked: function (event) {
        event.preventDefault();

        var $action = $(event.currentTarget);
        var type = $action.data('type') || 'button';

        switch (type) {
            case 'edit':
                this.trigger_up('open_record', {id: this.db_id, mode: 'edit'});
                break;
            case 'open':
                this.trigger_up('open_record', {id: this.db_id});
                break;
            case 'delete':
                this.trigger_up('kanban_record_delete', {id: this.db_id, record: this});
                break;
            case 'archive':
                this.trigger_up('kanban_record_archive');
                break;
            case 'action':
            case 'object':
                this.trigger_up('button_clicked', {
                    attrs: $action.data(),
                    record: this.state,
                });
                break;
            default:
                this.do_warn("Kanban: no action for type : " + type);
        }
    },
})
return MyKanbanRecord;
});