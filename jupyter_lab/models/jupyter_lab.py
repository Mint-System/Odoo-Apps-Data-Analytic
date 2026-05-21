# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class JupyterLab(models.Model):
    _name = "jupyter.lab"
    _description = "Jupyter Lab"

    name = fields.Char()
    path = fields.Char()
