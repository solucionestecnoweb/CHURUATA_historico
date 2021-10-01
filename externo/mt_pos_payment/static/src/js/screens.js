odoo.define('mt_pos_payment.screens', function (require) {
"use strict";

var PosBaseWidget = require('point_of_sale.BaseWidget');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var core = require('web.core');
var rpc = require('web.rpc');
var utils = require('web.utils');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;
 
var ReceiptScreenWidget = ScreenWidget.extend({
    template: 'ReceiptScreenWidget',
    show: function(){
        this._super();
        var self = this;
    },
    click_redirect: function() {
        location.href = self.pos.company.url_redirect;
    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.button.print_url').click(function(){
            self.click_redirect();
        });
    },
});
gui.define_screen({name:'receipt', widget: ReceiptScreenWidget});
return {
    ReceiptScreenWidget: ReceiptScreenWidget,
};
});
