# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name": "POS Stock",
    "summary": "The user can display the product quantities on the Odoo POS with the module. If set, The user cannot add out of stock products to the POS cart.",
    "category": "Point of Sale",
    "version": "1.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://store.webkul.com/Odoo-POS-Stock.html",
    "description": """Odoo POS Stock
Show product quantity in POS
Out of stock products
Out-of-stock products POS
Added product quantities
POS product stock
Show stock pos
Manage POS stock
Product management POS
""",
    "live_test_url": "http://odoodemo.webkul.com/?module=pos_stocks",
    "depends": ['point_of_sale','mrp'],
    "data": [
        'views/pos_config_view.xml',
        'views/template.xml',
    ],
    "qweb": ['static/src/xml/pos.xml'],
    "images": ['static/description/Banner.png'],
    "application": True,
    "installable": True,
    "auto_install": False,
    "price": 47,
    "currency": "EUR",
    "pre_init_hook": "pre_init_check",
}
