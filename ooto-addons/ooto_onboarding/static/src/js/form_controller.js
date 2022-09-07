odoo.define('ooto_onboarding.FormController', function (require) {
    "use strict";

    var formController = require('web.FormController');

    /*
    * Return kanban wiew of child tasks after saving new onboarding
    */
    formController.include({
        _onSave: function (ev) {
            // variable initialisation
            var self = this;
            var record = this.model.get(this.handle, {raw: true});
            var context = record.getContext();
            // check if all required field was filled
            var required_checked = this.check_required_fields(record);
            if (self.modelName === 'hr.employee' && required_checked && !record['data']['id']) {
                ev.stopPropagation(); // Prevent x2m lines to be auto-saved
                this._disableButtons();
                this.saveRecord().then(function(){
                    self._enableButtons.bind(this);
                    self._rpc({
                        model: 'employee.option',
                        method: 'get_wizard_view_id',
                        args: [record],
                        context: context
                    }).then(function (view_id) {
                        console.log(record['data']);
                        context['create_vals'] = record['data'];
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: 'employee.option',
                            name: _(' '),
                            view_type: 'form',
                            view_mode: 'form',
                            view_id: view_id,
                            target: 'new',
                            context: context,
                            views: [[false, 'form']]
                        });
                    });
                }).guardedCatch(this._enableButtons.bind(this));
            }
            else{
                return this._super.apply(this, arguments);
            }
        },
        /**
         * Check required fields values
         * @param record
         * @returns {boolean}
         */
        check_required_fields: function (record) {
            var fields = record['fieldsInfo']['form'];
            var datas = record['data'];
            var required_fields = [];
            for (var key in fields) {
                if (fields[key]['modifiersValue']) {
                    if (fields[key]['modifiersValue']['required'] === true) required_fields.push(key)
                }
            }
            for (let i = 0; i < required_fields.length; i++) {
                if (datas[required_fields[i]] === false) return false;
            }
            return true
        },
        saveRecord: function () {
            // variable initialisation
            var self = this;
            console.log(self.modelName)
            var record = this.model.get(this.handle, {raw: true});
            if (self.modelName === 'hr.onboarding' && isNaN(record.data.id)) {
                return self._super.apply(this, arguments).then(function (result) {
                    self.get_onboarding_task_action();
                    return result;
                });
//                return $.when(res);
            }
            else {
                return this._super.apply(this, arguments);
            }
        },

        get_onboarding_task_action: async function () {
            var self = this;
            this._rpc({
                model: 'hr.onboarding',
                method: 'get_onboarding_task_action',
                args: [this.getSelectedIds()],
            }).then(function (res) {
                self.do_action(res);
            });
        }
    });
});