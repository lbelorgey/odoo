# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    intrastat_product_origin_country_id = fields.Many2one(
        "res.country", string="Origin Country of Product"
    )
