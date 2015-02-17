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

import time
import pytz
from datetime import datetime
from tools import DEFAULT_SERVER_DATETIME_FORMAT

class pos_report_wizard(osv.osv_memory):
    _name = 'pos.report.wizard'
    _description = 'Wizard for POS report'
    
    _columns = {
                'user_ids': fields.many2many('res.users', 'user_wizard_rel', 'wizard_id', 'user_id', 'Partners'),
                'from_date': fields.date('From'),
                'to_date': fields.date('To'),
                }
    
    _defaults = {
                 'from_date': lambda *a: time.strftime('%Y-%m-%d'),
                 'to_date': lambda *a: time.strftime('%Y-%m-%d')
                 }
    
    def convert_from_local_datetime(self, cr, uid, date, hour, context=None):
        user_obj = self.pool.get('res.users').browse(cr, uid, uid, context)
        usr_zone = user_obj.context_tz or 'America/Hermosillo'
        zone = pytz.timezone(usr_zone)
        date_original = datetime.strptime(date + ' '+ hour, DEFAULT_SERVER_DATETIME_FORMAT)
        src_dt = zone.localize(date_original)
        date_local = src_dt.astimezone(pytz.utc)
        return date_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    
    def print_report(self, cr, uid, ids, context=None):
        data = {}
        data['form'] = self.read(cr, uid, ids, ['from_date', 'to_date'], context=context)[0]
        data['form']['user_ids'] = [uid]
        data['form']['from_date'] = self.convert_from_local_datetime(cr, uid, data['form']['from_date'], '00:00:00')
        data['form']['to_date'] = self.convert_from_local_datetime(cr, uid, data['form']['to_date'], '23:59:59')
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'pos.report',
                'datas': data,
               }
    
pos_report_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
