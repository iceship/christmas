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
from osv import osv, fields
import decimal_precision as dp

class product_product(osv.osv):
    _inherit = 'product.product'
    
    def _product_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        
        if context is None:
            context = {}
        quantity = context.get('quantity') or 1.0
        pricelist =context.get('pricelist', False)
        if not  pricelist:
            user_obj=self.pool.get('res.users').browse(cr, uid, uid, context=context)
            if user_obj.shop_id and user_obj.shop_id.pricelist_id :
                pricelist =user_obj.shop_id.pricelist_id.id
        partner = context.get('partner', False)
        if not pricelist:
            for product_obj in self.browse(cr, uid, ids, context=context):
                 
                 res[product_obj.id] = product_obj.list_price
        if pricelist:
            for id in ids:
                try:
                    price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist], id, quantity, partner=partner, context=context)[pricelist]
                   
                except:
                    price = 0.0
                res[id] = round(price,3)
                
        for id in ids:
            res.setdefault(id, 0.0)
        return res
    
    _columns = {
                'price': fields.function(_product_price, type='float', string='Pricelist', digits_compute=dp.get_precision('Sale Price')),
                'auto_produce': fields.boolean('Auto Produce', help="Create an production order from pos if product is Make to order and Produce")
                }
    
product_product()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: