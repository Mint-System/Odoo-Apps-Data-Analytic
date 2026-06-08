# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class JupyterNotebook(models.Model):
    _inherit = "jupyter.notebook"

    def action_open_run_wizard(self):
        """
        Open the run wizard with the current notebook pre-filled.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Run Jupyter Notebook",
            "res_model": "jupyter.notebook.run.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_notebook_id": self.id},
        }
