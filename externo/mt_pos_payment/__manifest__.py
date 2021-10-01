# -*- coding: utf-8 -*-
##############################################################################
#
#    MoviTrack
#    Copyright (C) 2020-TODAY MoviTrack.
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "PoS Custom Button ",
    'description': """
        Add payment button in PoS with company configuration to ser a URL without 
        modify the Code
    """,
    'author': 'MoviTrack.',
    'license': 'LGPL-3',
    'category': 'POS',
    'support': 'info@movitrack.co',
    'version': '13.0.1.0.0',
    'depends': ['point_of_sale','base','ext_extension_tpdv'],
    'data': [
        'views/assets.xml',
        'views/res_company_view.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
}
