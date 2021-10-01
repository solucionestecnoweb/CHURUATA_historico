odoo.define('mt_pos_payment.ReceiptScreenWidget', function (require) {
    'use strict';
    var screens = require('point_of_sale.screens');
    var ReceiptScreenWidget = screens.ReceiptScreenWidget;
    var rpc = require('web.rpc');

    ReceiptScreenWidget.include({
        click_redirect: function() {
            rpc.query({
                  model: 'res.company',
                  method: 'get_url_redirect',
                  args: [this.pos.company.id],
              }).then(function (url_redirect) {
                  location.href = url_redirect;
              });
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.button.print_url').click(function(){
                self.click_redirect();

            });
        },
        });
});