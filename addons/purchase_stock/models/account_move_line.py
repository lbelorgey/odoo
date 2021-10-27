# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.move.line'

    def _is_eligible_cogs_purchase(self):
        result = self._is_eligible_cogs()
        if result and not self.purchase_line_id:
            result = False
        return result
