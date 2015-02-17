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

from tools import amount_to_text_en
from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX
import netsvc
import decimal_precision as dp

class point_of_sale(osv.osv):
    _inherit = 'pos.order'
    
    def _get_order_ids(self, cr, uid, ids, context=None):
        pos_pool = self.pool.get('pos.order')
        pos_ids = pos_pool.search(cr, uid, [('company_id', 'in', ids)], context=context)
        return pos_ids
    
    def convert(self, cr, uid, ids, amount, company_id, context=None):
        company_obj = self.pool.get('res.company')
        amt_en = amount
        amt = ''
        context={}
        amount = float(amount)
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            currency = company.currency_id and company.currency_id or False
            if currency:
                if currency.name == 'USD':
                    currency_name = 'Dollars'
                else:
                    currency_name = currency.name
                if currency_name == 'MXN':
                    amt = amount_to_text_es_MX.get_amount_to_text(self, amount, 'es_cheque', currency_name)
                else:
                    amt = amount_to_text_en.amount_to_text(amount, 'en', currency_name)
                    if amt.endswith('Cents'):
                        amt = amt.replace('Cents', currency.sub_currency and currency.sub_currency or 'Cents')
                    else:
                        amt = amt.replace('Cent', currency.sub_currency and currency.sub_currency or 'Cent')
                 
        return amt
    
    def onchange_shop_id(self, cr, uid, ids, shop_id=False, context=None):
        res = {}
        shop_pool = self.pool.get('sale.shop')
        if shop_id:
            shop_obj = shop_pool.browse(cr, uid, shop_id, context=context)
            analytic_account_id = shop_obj.project_id and shop_obj.project_id.id or False
            res['value'] = {'analytic_account_id': analytic_account_id}
        return res
    
    def _get_analytic_account(self, cr, uid, ids, context=None):
        analytic_account_id = False
        shop_pool = self.pool.get('sale.shop')
        shop_id = self._default_shop(cr, uid, context=context)
        if shop_id:
            shop_obj = shop_pool.browse(cr, uid, shop_id, context=context)
            analytic_account_id = shop_obj and shop_obj.project_id and shop_obj.project_id.id or False
        return analytic_account_id
    
    def _amount_in_words(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for pos_obj in self.browse(cr, uid, ids, context=context):
            currency = pos_obj.company_id and pos_obj.company_id.currency_id and pos_obj.company_id.currency_id
            res[pos_obj.id] = ""
            result = self._amount_all(cr, uid, ids, name, args, context=context)
            data = result.get(pos_obj.id, {})
            amount_total = data.get('amount_total', 0.00)
            discount_amount = pos_obj.discount_amount or 0.00
            amount_total = amount_total - discount_amount
            if currency:
                amount_total = cur_obj.round(cr, uid, currency, amount_total)
                amount_in_words = self.convert(cr, uid, ids, amount_total, pos_obj.company_id.id, context=context)
                res[pos_obj.id] = amount_in_words
        return res
    
    def _get_partner_address(self, cr, uid, ids, partner_id=False, context=None):
        partner_pool = self.pool.get('res.partner')
        address_pool = self.pool.get('res.partner.address')
        state_pool = self.pool.get('res.country.state')
        address = ''
        if partner_id:
            address = partner_pool.address_get(cr, uid, [partner_id])
            address_id = address.get('default', False)
            if address_id:
                address = ''
                state_code = ''
                address_data = address_pool.read(cr, uid, address_id, ['street',
                                                                       'street1',
                                                                       'street2',
                                                                       'street3',
                                                                       'street4',
                                                                       'zip',
                                                                       'city',
                                                                       'city2',
                                                                       'state_id',
                                                                       'country_id'])
                if address_data.get('state_id', False):
                    state_code = address_data.get('state_id', False)[1]
                elems = [
                         address_data.get('street',False),
                         address_data.get('street3',False),
                         address_data.get('street4',False),
                         address_data.get('street2',False),
                         address_data.get('zip',False),
                         address_data.get('city2',False),
                         address_data.get('city',False),
                         address_data.get('country_id',False) and address_data.get('country_id',False)[1] or False,
                         state_code,
                         ]
                address = ', '.join(filter(bool, elems))
        return address
        
    def _get_address(self, cr, uid, ids, name, args, context=None):
        res = {}
        for pos_obj in self.browse(cr, uid, ids, context=context):
            partner_id = pos_obj.partner_id and pos_obj.partner_id.id or False
            address = self._get_partner_address(cr, uid, ids, partner_id, context=context)
            res[pos_obj.id] = address
        return res
    
    def _get_company_address(self, cr, uid, ids, name, args, context=None):
        res = {}
        for pos_obj in self.browse(cr, uid, ids, context=context):
            address = ''
            company_partner_id = pos_obj.company_id and pos_obj.company_id.partner_id and pos_obj.company_id.partner_id.id or False
            if company_partner_id:
                address = self._get_partner_address(cr, uid, ids, company_partner_id, context=context)
            res[pos_obj.id] = address
        return res
    
    def _get_warehouse_address(self, cr, uid, ids, name, args, context=None):
        res = {}
        for pos_obj in self.browse(cr, uid, ids, context=context):
            address_ele = []
            res[pos_obj.id] = ""
            warehouse_obj = pos_obj.shop_id.warehouse_id
            warehouse_owner_address = warehouse_obj.partner_address_id or False
            if warehouse_owner_address:
                if warehouse_owner_address.street:
                    address_ele.append(warehouse_owner_address.street)
                if warehouse_owner_address.street3:
                    address_ele.append(warehouse_owner_address.street3)
                if warehouse_owner_address.street4:
                    address_ele.append(warehouse_owner_address.street4)
                if warehouse_owner_address.street2:
                    address_ele.append(warehouse_owner_address.street2)
                if warehouse_owner_address.zip:
                    address_ele.append(warehouse_owner_address.zip)
                if warehouse_owner_address.city2:
                    address_ele.append(warehouse_owner_address.city2)
                if warehouse_owner_address.city:
                    address_ele.append(warehouse_owner_address.city)
                if warehouse_owner_address.country_id:
                    address_ele.append(warehouse_owner_address.country_id.name)
                if warehouse_owner_address.state_id:
                    address_ele.append(warehouse_owner_address.state_id.name)
                res[pos_obj.id] = ', '.join(address_ele)
        return res
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = super(point_of_sale, self)._amount_all(cr, uid, ids, name, args, context=context)
        currency_pool = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            order_data = res.get(order.id, {})
            amount_paid = 0.00
            for payment in order.statement_ids:
                rate = payment.statement_id and payment.statement_id.curr_rate or 1.00
                amount_paid += payment.amount / rate
            order_data['amount_paid'] =  amount_paid
        return res
    
    _columns = {
                'create_uid': fields.many2one('res.users', 'Created User'),
                'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
                'amount_in_words': fields.function(_amount_in_words, string='Amount In Words', type='char', size=128, store=True),
                'vat': fields.related('company_id', 'partner_id', 'vat', type='char', size=128, string='VAT', store=True),
                'partner_address': fields.function(_get_address, string='Partner Address', type='char',
                                                      size=128, readonly=True, store=True),
                'company_address': fields.function(_get_company_address, string='Company Address', type='char',
                                                      size=128, readonly=True, store=True),
                'warehouse_address': fields.function(_get_warehouse_address, string='Warehouse Address', type='char',
                                                      size=128, readonly=True, store=True),
                'company_country': fields.related('company_id', 'partner_id', 'address', 'country_id', 'name',
                                                  type="char", size=128, string="Company Country", store=True),
                'company_state': fields.related('company_id', 'partner_id', 'address', 'state_id', 'code',
                                                type="char", size=64, string="Company State", store=True),
                'discount_amount': fields.float('Discount'),
                'discount_percentage': fields.float('Discount (%)'),
                'refund': fields.boolean('Refund?'),
                'frontname': fields.char('Front End Ref', size=128, help="In case of offline mode, this number will be printed in receipt."),
                'amount_paid': fields.function(_amount_all, string='Paid', states={'draft': [('readonly', False)]},
                                               readonly=True, multi='all'),
                'amount_tax': fields.function(_amount_all, string='Taxes', digits_compute=dp.get_precision('Point Of Sale'), multi='all'),
                'amount_total': fields.function(_amount_all, string='Total', multi='all'),
                'amount_return': fields.function(_amount_all, 'Returned', digits_compute=dp.get_precision('Point Of Sale'), multi='all'),
                }
    
    _default = {
                'analytic_account_id': _get_analytic_account
                }
    
    def refund(self, cr, uid, ids, context=None):
        res = super(point_of_sale, self).refund(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'refund': True}, context=context)
        return res
    
    def get_price(self, cr, uid, product_id, qty=0):
        product_pool = self.pool.get('product.product')
        context = {
                   'quantity': qty,
                   }
        product_data = product_pool._product_price(cr, uid, [product_id], name=False, arg=False, context=context)
        product_price = product_data.get(product_id, 0.00)
        return product_price
    
    def create_from_ui(self, cr, uid, orders, context=None):
        user_pool = self.pool.get('res.users')
        cur_obj = self.pool.get('res.currency')
        order_obj = self.pool.get('pos.order')
        list = []
        for order in orders:
            statement_ids = order.pop('statement_ids')
            frontname =  order['name']
            if order['partner_id'] == 0 or order['partner_id'] == '0':
                order['partner_id'] = False
            if order['user_id'] == 0 or order['user_id'] == '0':
                order['user_id'] = False
            amount = order.get('amount_total', False)
            seq = self.pool.get('ir.sequence').get(cr, uid, 'pos.order')
            order['name'] = seq
            if uid:
                if not order.get('user_id', False):
                    order['user_id'] = uid
                user_obj = user_pool.browse(cr, uid, int(uid), context=context)
                discount_allowable = user_obj.discount_percent or 0.00
                discount = order.get('discount_percentage', 0.00)
                if float(discount) > float(discount_allowable):
                    msg = []
                    msg.append('percent')
                    msg.append(discount_allowable)
                    return msg
                shop_id = user_obj and user_obj.shop_id and user_obj.shop_id.id or False
                if shop_id:
                    analytic_account_id = user_obj.shop_id.project_id and user_obj.shop_id.project_id.id or False
                    order['shop_id'] = shop_id
                    if analytic_account_id:
                        order['analytic_account_id'] = analytic_account_id
            order['frontname'] = frontname
            order_id = self.create(cr, uid, order, context)
            list.append(order_id)
            for satement in statement_ids:
                data = {
                    'journal': satement[2]['journal_id'],
                    'amount': satement[2]['amount'] * satement[2]['curr_rate'],
                    'payment_name': order['name'],
                    'payment_date': satement[2]['name'],
                }
                order_obj.add_payment(cr, uid, order_id, data, context=context)
        return list
    
    def create_discount_invoice_line(self, cr, uid, ids, invoice_id, disc_amount, shop, partner, context=None):
        res = {}
        if shop:
            discount_product = shop.disc_product_id and shop.disc_product_id.id or False
            account_id = shop.disc_product_id.property_account_income.id
            if not account_id:
                account_id =  shop.disc_product_id.categ_id.property_account_income_categ.id
            if partner:
                account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id)
            res = {
                   'name': "Discount",
                   'invoice_id': invoice_id,
                   'uos_id': shop.disc_product_id and shop.disc_product_id.uos_id and \
                                shop.disc_product_id.uos_id.id or False,
                   'product_id': shop.disc_product_id.id,
                   'account_id': account_id,
                   'price_unit': disc_amount * -1,
                   'quantity': 1,
                   }
        return res
        
    def action_invoice(self, cr, uid, ids, context=None):
        invoice_pool = self.pool.get('account.invoice')
        invoice_line_pool = self.pool.get('account.invoice.line')
        res = super(point_of_sale, self).action_invoice(cr, uid, ids, context=context)
        for pos_obj in self.browse(cr, uid, ids, context=context):
            analytic_account_id = pos_obj.analytic_account_id and pos_obj.analytic_account_id.id or False
            invoice_id = res.get('res_id', False)
            if invoice_id:
                invoice_obj = invoice_pool.browse(cr, uid, invoice_id, context=context)
                invoice_line_ids = [x.id for x in invoice_obj.invoice_line if invoice_obj.invoice_line]
                invoice_line_pool.write(cr, uid, invoice_line_ids, {'account_analytic_id': analytic_account_id},
                                        context=context)
                if pos_obj.discount_amount > 0.00:
                    vals = self.create_discount_invoice_line(cr, uid, ids, invoice_id, pos_obj.discount_amount,
                                                            pos_obj.shop_id, pos_obj.partner_id, context=context)
                    invoice_line_pool.create(cr, uid, vals, context=context)
        return res
    
    def test_paid(self, cr, uid, ids, context=None):
        res = super(point_of_sale, self).test_paid(cr, uid, ids, context=context)
        if not res:
            for order in self.browse(cr, uid, ids, context=context):
                if (not order.lines) or (not order.statement_ids) or \
                    (round(order.amount_total, 2)-(round(order.amount_paid, 2) + round(order.discount_amount, 2))> 0.00001):
                    return False
                else:
                    return True
        return res
    
    def create_picking(self, cr, uid, ids, context=None):
        procurement_pool = self.pool.get('procurement.order')
        mrp_pool = self.pool.get('mrp.production')
        production_ids = []
        wf_service = netsvc.LocalService("workflow")
        for pos_obj in self.browse(cr, uid, ids, context=context):
            for pos_line_obj in pos_obj.lines:
                if pos_line_obj.product_id.procure_method == 'make_to_order' and \
                                        pos_line_obj.product_id.supply_method == 'produce' and \
                                        pos_line_obj.product_id.auto_produce == True:
                    vals = {
                            'company_id' : pos_obj.company_id.id,
                            'name': pos_obj.name,
                            'origin': pos_obj.name,
                            'date_planned': pos_obj.date_order,
                            'product_id': pos_line_obj.product_id.id,
                            'product_qty': pos_line_obj.qty,
                            'product_uom': pos_line_obj.product_id.uom_id.id,
                            'product_uos_qty': pos_line_obj.qty,
                            'product_uos': pos_line_obj.product_id.uos_id.id,
                            'location_id': pos_line_obj.order_id.shop_id.warehouse_id.lot_input_id.id,
                            'procure_method': 'make_to_order',
                            'note': "Procurement created from POS"
                            }
                    proc_id = procurement_pool.create(cr, uid, vals, context=context)
                    wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                    mrp_ids = mrp_pool.search(cr, uid, [
                                                        ('origin', '=', pos_obj.name),
                                                        ('product_id', '=', pos_line_obj.product_id.id),
                                                        ('product_qty', '=', pos_line_obj.qty)
                                                        ], context=context)
                    production_ids.extend(mrp_ids)
        if production_ids:
            for production_obj in mrp_pool.browse(cr, uid, production_ids, context=context):
                wf_service.trg_validate(uid, 'mrp.production', production_obj.id, 'button_produce', cr)
                mrp_pool.action_produce(cr, uid, production_obj.id, production_obj.product_qty,
                                        'consume_produce', context = None)
                wf_service.trg_validate(uid, 'mrp.production', production_obj.id, 'button_produce_done', cr)
        res = super(point_of_sale, self).create_picking(cr, uid, ids, context=context)
        return res
    
point_of_sale()

class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'
    
    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        result = super(pos_order_line, self)._amount_line_all(cr, uid, ids, field_names, arg, context=context)
        res = dict([(i, {}) for i in ids])
        account_tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        company_pool = self.pool.get('res.company')
        user_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = user_obj.company_id
        company_ids = company_pool.search(cr, uid, [('parent_id', 'child_of', company_id.id)], context=context)
        for line in self.browse(cr, uid, ids, context=context):
            taxes = line.product_id.taxes_id
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes_id = [x for x in line.product_id.taxes_id if (x.company_id == False or x.company_id in company_ids)]
            taxes = account_tax_obj.compute_all(cr, uid, taxes_id, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id]['price_subtotal'] = result[line.id]['price_subtotal']
            res[line.id]['price_subtotal_incl'] = cur_obj.round(cr, uid, cur, taxes['total_included'])
        return res
    
    _columns = {
                'price_subtotal': fields.function(_amount_line_all, multi='pos_order_line_amount',
                                                  string='Subtotal w/o Tax', store=True),
                'price_subtotal_incl': fields.function(_amount_line_all, multi='pos_order_line_amount',
                                                       string='Subtotal', store=True),
                }
    
pos_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
