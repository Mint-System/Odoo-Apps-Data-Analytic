# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


class JupyterNotebookRunWizard(models.TransientModel):
    _name = "jupyter.notebook.run.wizard"
    _description = "Jupyter Notebook Run Wizard"

    notebook_id = fields.Many2one("jupyter.notebook", string="Notebook", required=True)
    lab_id = fields.Many2one("jupyter.lab", string="Lab", related="notebook_id.lab_id", readonly=True)
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
    datas = fields.Binary(string="Upload File")
    datas_fname = fields.Char(string="Filename")
    values = fields.Text(string="Values", help="JSON object with parameters for the notebook.")

    def action_run(self):
        """
        Create a run and execute it.
        """
        self.ensure_one()

        if not self.notebook_id:
            raise UserError(_("Please select a notebook."))

        attachment_id = self.attachment_id.id
        if self.datas:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": self.datas_fname or "upload",
                    "datas": self.datas,
                }
            )
            attachment_id = attachment.id

        run = self.env["jupyter.notebook.run"].create(
            {
                "name": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "notebook_id": self.notebook_id.id,
                "attachment_id": attachment_id,
                "values": self.values,
            }
        )
        run.action_run()

        # Return an action to open the run record
        return {
            "type": "ir.actions.act_window",
            "name": "Notebook Run",
            "res_model": "jupyter.notebook.run",
            "view_mode": "form",
            "res_id": run.id,
            "target": "current",
        }
