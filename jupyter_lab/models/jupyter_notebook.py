# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from pathlib import Path

from odoo import fields, models
from odoo.tools import config


class JupyterNotebook(models.Model):
    _name = "jupyter.notebook"
    _description = "Jupyter Notebook"

    name = fields.Char(required=True)
    lab_id = fields.Many2one("jupyter.lab", string="Lab", required=True, ondelete="cascade")
    local_path = fields.Char(compute="_compute_local_path")
    url = fields.Char(compute="_compute_url")
    lab_state = fields.Selection(related="lab_id.state")

    def _compute_local_path(self):
        for notebook in self:
            notebook.local_path = str(Path(notebook.lab_id.local_path) / notebook.name)

    def _compute_url(self):
        """
        Generate notebook url based on lab token.
        """
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for notebook in self:
            if config["proxy_mode"]:
                notebook.url = f"{base_url}/notebooks/{notebook.name}?token={notebook.lab_id.token}"
            else:
                notebook.url = f"http://localhost:8888/notebooks/{notebook.name}?token={notebook.lab_id.token}"

    def action_open(self):
        """
        Open notebook in Jupyter Lab.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.url,
            "target": "new",
        }
