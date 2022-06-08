/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_stock.BaseWidget',function(require) {
    "use strict";
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    
    PosBaseWidget.include({
        set_stock_qtys: function(result){
            var self = this;
            if(!self.chrome.screens){
                $.unblockUI();
                return;
            }
            self.chrome.screens.products.product_categories_widget.reset_category();
            var all = $('.product');
            $.each(all, function(index, value){
                var product_id = $(value).data('product-id');
                var stock_qty = result[product_id];
                $(value).find('.qty-tag').html(stock_qty);
            });
            $.unblockUI();
        },
        get_information: function(wk_product_id) {
            self = this;
            if (self.pos.get('wk_product_qtys'))
                return self.pos.get('wk_product_qtys')[wk_product_id];
        },
        wk_change_qty_css: function() {
            self = this;
            var wk_order = self.pos.get('orders');
            var wk_p_qty = new Array();
            var wk_product_obj = self.pos.get('wk_product_qtys');
            if (wk_order) {
                for (var i in wk_product_obj)
                    wk_p_qty[i] = self.pos.get('wk_product_qtys')[i];
                for (var i = 0; i < wk_order.length; i++) {
                    if(!wk_order.models[i].is_return_order){
                        var wk_order_line = wk_order.models[i].get_orderlines();
                        for (var j = 0; j < wk_order_line.length; j++) {
                            if(!wk_order_line[j].stock_location_id) 
                                wk_p_qty[wk_order_line[j].product.id] = wk_p_qty[wk_order_line[j].product.id] - wk_order_line[j].quantity;                       
                            var qty = wk_p_qty[wk_order_line[j].product.id];
                            if (qty)
                                $("#qty-tag" + wk_order_line[j].product.id).html(qty);
                            else
                                $("#qty-tag" + wk_order_line[j].product.id).html('0');
                        }
                    }
                }
            }
        }
    })
});