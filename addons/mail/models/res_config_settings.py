# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from werkzeug import urls

from odoo import api, fields, models, tools


class ResConfigSettings(models.TransientModel):
    """ Inherit the base settings to add a counter of failed email + configure
    the alias domain. """
    _inherit = 'res.config.settings'

    fail_counter = fields.Integer('Fail Mail', compute="_compute_fail_counter")
    alias_domain = fields.Char(
        'Alias Domain', config_parameter='mail.catchall.domain',
        help="If you have setup a catch-all email domain redirected to the Odoo server, enter the domain name here.")

    def _compute_fail_counter(self):
        previous_date = fields.Datetime.now() - datetime.timedelta(days=30)

        self.fail_counter = self.env['mail.mail'].sudo().search_count([
            ('date', '>=', previous_date),
            ('state', '=', 'exception'),
        ])
