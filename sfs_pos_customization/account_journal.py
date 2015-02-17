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

class account_journal(osv.osv):
    _inherit='account.journal'
    
    def _get_curr_rate(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        currency_pool = self.pool.get('res.currency')
        for journal_obj in self.browse(cr, uid, ids, context=context):
            res[journal_obj.id] = {}
            user_obj = self.pool.get('res.users').browse(cr, uid, uid)
            shop_currency = user_obj.shop_id and user_obj.shop_id.pricelist_id.currency_id or \
                                    user_obj.company_id.currency_id
            company_currency = user_obj.company_id.currency_id
            journal_currency = journal_obj.currency and journal_obj.currency or company_currency
            rate = currency_pool._get_conversion_rate(cr, uid, shop_currency,
                                                     journal_currency, context=context)
            comp_rate = currency_pool._get_conversion_rate(cr, uid, shop_currency,
                                                     company_currency, context=context)
            res[journal_obj.id]['curr_rate'] = rate
            res[journal_obj.id]['comp_curr_rate'] = comp_rate
        return res
    
    _columns = {
                'curr_rate': fields.function(_get_curr_rate, string='Currency Rate', multi='rate'),
                'comp_curr_rate': fields.function(_get_curr_rate, string='Company currency rate', multi='rate')
                }
account_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: