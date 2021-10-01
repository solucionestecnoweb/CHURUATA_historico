
{
    "name": """POS: Mostrar Dualidad de moneda""",
    "summary": """Agrega el precio de otra moneda en los productos en POS""",
    "category": "Point Of Sale",
    "version": "13.0.1.0.0",
    "application": False,
    'author': 'José Luis Vizcaya López / Modificado por: Darrell Sojo',
    'company': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'maintainer': 'Ing. Darrell Sojo',
    'website': 'http://soluciones-tecno.com/',
    "depends": ["point_of_sale", "stock","l10n_ve_res_currency"],
    "data": ["views/data.xml", "views/views.xml"],
    "qweb": ["static/src/xml/pos.xml"],
    #"license": "OPL-1",
    'images': [
        'static/description/thumbnail.png',
    ],
    "price": 10,
    "currency": "USD",
    "auto_install": False,
    "installable": True,
}
