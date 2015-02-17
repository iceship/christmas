# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
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

from osv import osv, fields

from tools.translate import _

class sale_shop(osv.osv):
    _inherit = 'sale.shop'
    _columns = {
                'users_ids': fields.many2many('res.users', 'shop_users_rel', 'shop_id', 'user_id', 'Users'),
                'disc_product_id': fields.many2one('product.product', 'Discount Product', required=False),
                'user_id': fields.related('users_ids','id',type='many2one', relation='res.users', string='User'),
                'default_partner_id': fields.many2one('res.partner', 'Default POS Partner')
                }
sale_shop()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
