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

from osv import osv

from tools.translate import _

class pos_make_payment(osv.osv_memory):
    _inherit = 'pos.make.payment'
    
    def check(self, cr, uid, ids, context=None):
        user_pool = self.pool.get('res.users')
        pos_pool = self.pool.get('pos.order')
        if uid and context.get('active_id', False):
            user_obj = user_pool.browse(cr, uid, uid, context=context)
            pos_obj = pos_pool.browse(cr, uid, context['active_id'], context=context)
            discount_per_user = user_obj.discount_percent or 0.00
            discount = pos_obj.discount_percentage or 0.00
            if discount > discount_per_user:
                raise osv.except_osv(_('Discount error'),
                                     _('Discount Percentage exceeds your allowed limit'))
        res = super(pos_make_payment, self).check(cr, uid, ids, context=context)
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        res = super(pos_make_payment, self).print_report(cr, uid, ids, context=context)
        if res.get('report_name', False):
            res['report_name'] = 'pos.ticket.report'
        return res
    
pos_make_payment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
