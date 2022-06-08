/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_stock.popups', function (require) {
    "use strict";
    
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    
    var OutOfStockMessagePopup = PopupWidget.extend({
        template: 'OutOfStockMessagePopup',
        show:function(options){
            var self = this;
            this.options = options || ''; 
            self._super(options);
        }
    });
    gui.define_popup({ name: 'out_of_stock', widget: OutOfStockMessagePopup });
    
    return OutOfStockMessagePopup;
});