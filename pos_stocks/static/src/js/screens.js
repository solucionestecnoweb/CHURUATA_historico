/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_stock.screens', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    screens.ProductScreenWidget.include({
        show: function(reset){
            this._super(reset);
            this.pos.chrome.set_stock_qtys(this.pos.get('wk_product_qtys'));
            this.pos.chrome.wk_change_qty_css();
        },
    });

    screens.NumpadWidget.include({
        start: function() {
            var self = this;
            this._super();
            this.$el.find('.numpad-backspace').on('update_buffer',function(){
                return self.state.delete_last_char_of_buffer();
            });
        }
    });
});