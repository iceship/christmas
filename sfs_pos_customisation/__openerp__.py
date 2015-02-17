# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name" : "Pos customisation",
    "version" : "3.8",
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    "category" : "Generic Modules",
    "depends" : [
               "point_of_sale",
               "l10n_mx_invoice_amount_to_text",
               "mrp",
               "mrp_jit",
               "account"
    ],
    "description": """
       POS Customisation
    """,
    'init_xml': [],
    'update_xml': [
                   "res_currency_view.xml",
                   "users_view.xml",
                   "point_of_sale_view.xml",
                   "report/pos_report.xml",
                   "report/pos_order_report_view.xml",
                   "wizard/pos_report_wizard_view.xml",
                   "product_view.xml",
                   "sale_shop_view.xml",
                   "pos_menu_access.xml",
                   "pos_data.xml",
                   "security/pos_security.xml"
    ],
    'demo_xml': [
    ],
    'test': [

    ],
    'installable': True,
    'active': False,
    'complexity':'easy'
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
