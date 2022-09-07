odoo.define('ooto_onboarding.basicFields', function (require) {
    "use strict";

    /*
    * Haingoniaina extend : change max_upload_size task onboarding
    */

    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    var FieldBinaryFile =  basic_fields.FieldBinaryFile;


     var FieldBinaryFileR = FieldBinaryFile.extend({
        init: function () {
            this._super.apply(this, arguments);
            var self = this;
             if (self.model === 'hr.onboarding.task'){
                this.max_upload_size = 200 * 1024 * 1024;
             }
        }
    });


registry
    .add('binary', FieldBinaryFileR);

});


//    var FieldBinaryImage = basic_fields.FieldBinaryImage;

//    var FieldBinaryImageR = FieldBinaryImage.extend({
//        init: function () {
//            this._super.apply(this, arguments);
//            var self = this;
//             if (self.model === 'hr.onboarding.task'){
//                console.log('FieldBinaryImage');
//                console.log(this);
//                this.max_upload_size = 200 * 1024 * 1024;
//             }
//        }
//    });

//    .add('image', FieldBinaryImageR)