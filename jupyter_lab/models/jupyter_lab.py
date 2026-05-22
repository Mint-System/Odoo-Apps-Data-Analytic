# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import secrets
from pathlib import Path

from odoo import fields, models
from odoo.tools import config

_logger = logging.getLogger(__name__)


class JupyterLab(models.Model):
    _name = "jupyter.lab"
    _description = "Jupyter Lab"

    name = fields.Char()
    local_path = fields.Char(compute="_compute_local_path", store="True")
    url = fields.Char(compute="_compute_url")
    pid = fields.Integer(readonly=True)
    token = fields.Char(compute="_compute_token", store=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("running", "Running"),
        ],
        readonly=True,
        copy=False,
        default="draft",
    )

    def _compute_url(self):
        """
        Generate url of jupyter lab server.
        Use web.base.url and proxy_mode config.
        Local: http://localhost:8069 -> http://localhost:8888/lab?token=<token>
        Proxy: https://odoo.example.com -> https://odoo.example.com/lab?token=<token>
        """
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if config["proxy_mode"]:
            for lab in self:
                lab.url = f"{base_url}/lab?token={lab.token}"
        else:
            for lab in self:
                lab.url = f"http://localhost:8888/lab?token={lab.token}"

    def _compute_local_path(self):
        slugify = self.env["ir.http"]._slugify
        for lab in self:
            lab.local_path = Path(config["data_dir"]) / "jupyter_lab" / slugify(lab.name)

    def _compute_token(self):
        for lab in self:
            lab.token = secrets.token_hex(16)

    def action_initialize(self):
        """
        Create juypter lab directory and config file.
        Copy startup script and main.ipynb template.
        """
        return

    def action_start(self):
        """
        Launch jupyter lab in directory. Ensure no other juypter lab is running.
        Pass current user uid to startup script. Store pid of process.
        """
        return

    def action_stop(self):
        """
        Stop juypter lab server.
        """
        return
