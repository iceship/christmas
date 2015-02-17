# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 SF Soluciones.
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

import time

from report import report_sxw

class pos_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(pos_report, self).__init__(cr, uid, name, context=context)
        self.pos_line_obj = []
        self.user_id = 0
        self.res = {}
        self.domain = []
        self.localcontext.update({
                                  'time': time,
                                  'res': self._get_res_data,
                                  'get_object': self._get_object,
                                  'get_pos_line': self._get_pos_line,
                                  'get_amount_total': self._get_amount_total,
                                  'get_refund_amount': self._get_refund_amount,
                                  'get_journal_line_data': self._get_journal_line_data,
                                  })
    def _get_object(self, data):
        user_pool = self.pool.get('res.users')
        user_ids = data['form']['user_ids']
        user_obj = user_pool.browse(self.cr, self.uid, user_ids, context={})
        self.domain = []
        if data['form']['from_date']:
            cond = ('date_order', '>=', data['form']['from_date'])
            self.domain.append(cond)
        if data['form']['to_date']:
            cond = ('date_order', '<=', data['form']['to_date'])
            self.domain.append(cond)
        return user_obj
        
    def _get_pos_line(self, user_id):
        if not self.pos_line_obj or self.user_id != user_id:
            self.pos_line_obj = []
            self.user_id = user_id
            pos_pool = self.pool.get('pos.order')
            cond = [('user_id', '=', user_id), ('state', 'not in', ('draft', 'cancel'))]
            cond.extend(self.domain)
            pos_ids = pos_pool.search(self.cr, self.uid, cond, context={})
            for pos_obj in pos_pool.browse(self.cr, self.uid, pos_ids, context={}):
                order_name = pos_obj.name
                if not order_name.endswith('REFUND'):
                    self.pos_line_obj.extend(pos_obj.lines)
        return self.pos_line_obj
    
    def _get_amount_total(self, user_id):
        amount_total = 0.00
        if not self.pos_line_obj or self.user_id != user_id:
            self._get_pos_line(user_id)
            self.user_id = user_id
        for pos_line in self.pos_line_obj:
            amount_total += pos_line.price_subtotal_incl
        return amount_total
    
    def _get_refund_amount(self, user_id):
        pos_pool = self.pool.get('pos.order')
        amount_refund = 0.00
        if not self.pos_line_obj or self.user_id != user_id:
            self._get_pos_line(user_id)
            self.user_id = user_id
        pos_line_ids = [x.order_id.id for x in  self.pos_line_obj]
        cond = [('user_id', '=', user_id), ('state', 'not in', ('draft', 'cancel')), ('id', 'not in', pos_line_ids)]
        cond.extend(self.domain)
        pos_line_refund_ids = pos_pool.search(self.cr, self.uid, cond, context={})
        for pos_obj in pos_pool.browse(self.cr, self.uid, pos_line_refund_ids, context={}):
            pos_lines = pos_obj.lines
            for lines in pos_lines:
                amount_refund += lines.price_subtotal_incl
        return amount_refund
    
    def _get_journal_line_data(self, user_id):
        res = {}
        if not self.pos_line_obj or self.user_id != user_id:
            self._get_pos_line(user_id)
            self.user_id = user_id
        for line in self.pos_line_obj:
            order_journal = line.order_id.sale_journal.name
            if not res.get(order_journal, False):
                res[order_journal] = 0.00
            res[order_journal] += line.price_subtotal_incl
            self.res = res
        return res
    
    def _get_res_data(self):
        return self.res
    
report_sxw.report_sxw('report.pos.report', 'pos.order', 'addons/sfs_pos_customization/report/pos_report.rml',
                      parser=pos_report, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
