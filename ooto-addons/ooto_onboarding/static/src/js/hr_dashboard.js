odoo.define('ooto_onboarding.dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var HrDashboardView = AbstractAction.extend({
    init: function(parent, context) {
        this._super(parent, context);
        var employee_data = [];
        var self = this;
        if (context.tag == 'ooto_onboarding.dashboard') {
            self._rpc({
                model: 'hr.dashboard',
                method: 'get_onboarding_info',
            }, []).then(function(result){
                self.employee_data = result
                if(self.employee_data){
                    self.render_dashboards();
                    self.render_graphs();
                    self.href = window.location.href;
                }
            })

//            .done(function(){
//                self.render();
//                self.href = window.location.href;
//            });
        }
    },

    willStart: function() {
        console.log("WILLSTART FUNCTION")
        var self = this;
        return $.when(ajax.loadLibs(this), this._super());
    },

    start: function() {
        console.log("START FUNCTION")
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            console.log('====================');
//            self.update_cp();
//            self.render_dashboards();
//            self.render_graphs();
//            self.$el.parent().addClass('oe_background_grey');
        });
    },

    render_dashboards: function() {console.log("RENDER_DASHBOARD")
        var super_render = this._super;
        var self = this;
        var hr_dashboard = QWeb.render('ooto_onboarding.dashboard',{widget: self});
        $( ".o_hr_dashboard" ).addClass( "o_hidden" );
        $(hr_dashboard).prependTo(self.$el);
        return hr_dashboard
    },

    reload: function () {
            window.location.href = this.href;
    },

    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },

    render_graphs: function(){console.log("RENDER_GRAPHS")
        var self = this
        var ctx = this.$el.find('#myChart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        //Pie Chart
        var piectx = this.$el.find('#achievementtaskchart');
        bg_color_list = []
        for (var i=0;i<=[5,9].length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.employee_data.task_data_value,
                    backgroundColor: bg_color_list,
                    label: 'Achievement task'
                }],
                labels:self.employee_data.task_data_label,
            },
            options: {
                responsive: true
            }
        });
        var periodpiectx = this.$el.find('#periodtaskchart');
        bg_color_list = []
        for (var i=0;i<=self.employee_data.period_data_value.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var periodpieChart = new Chart(periodpiectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.employee_data.period_data_value,
                    backgroundColor: bg_color_list,
                    label: 'Period task'
                }],
                labels:self.employee_data.period_data_label,
            },
            options: {
                responsive: true
            }
        });
    },

});
core.action_registry.add('ooto_onboarding.dashboard', HrDashboardView);
return HrDashboardView;
});
