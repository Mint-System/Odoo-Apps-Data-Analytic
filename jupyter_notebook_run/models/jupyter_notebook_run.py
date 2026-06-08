# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class JupyterNotebookRun(models.Model):
    _name = "jupyter.notebook.run"
    _description = "Jupyter Notebook Run"
    _order = "create_date desc"

    name = fields.Char(required=True, default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    notebook_id = fields.Many2one("jupyter.notebook", string="Notebook", required=True, ondelete="cascade")
    lab_id = fields.Many2one("jupyter.lab", string="Lab", related="notebook_id.lab_id", store=True, readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("running", "Running"),
            ("success", "Success"),
            ("error", "Error"),
        ],
        default="draft",
        readonly=True,
    )
    output = fields.Text(readonly=True)
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
    values = fields.Text(string="Values", help="JSON object with parameters for the notebook.")

    def action_reset(self):
        """
        Reset the run to draft state and clear the output.
        """
        self.ensure_one()
        self.write({"state": "draft", "output": False})

    def action_run(self):
        """
        Execute the notebook run with papermill.
        Copy attachment to lab folder, run papermill, capture output.
        """
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("A run can only be started from the Draft state."))
        notebook = self.notebook_id
        lab = self.lab_id

        if not notebook or not lab:
            raise UserError(_("Notebook and lab must be set to run."))

        notebook_path = Path(notebook.local_path)
        lab_path = Path(lab.local_path)

        # Copy attachment if provided
        if self.attachment_id:
            attachment_path = lab_path / self.attachment_id.name
            try:
                with open(attachment_path, "wb") as f:
                    f.write(self.attachment_id.raw)
            except OSError as e:
                _logger.error("Failed to write attachment to %s: %s", attachment_path, e)
                self.output = f"Failed to copy attachment: {e}"
                self.state = "error"
                return

        # Build papermill command
        cmd = [
            "papermill",
            "--log-output",
            str(notebook_path),
            str(notebook_path),
        ]

        if self.values:
            try:
                params = json.loads(self.values)
                if not isinstance(params, dict):
                    raise ValueError
            except (json.JSONDecodeError, ValueError):
                raise UserError(_("Values must be a valid JSON object."))
            for key, value in params.items():
                cmd.extend(["-p", key, str(value)])

        self.state = "running"
        self.output = ""

        # Prepare environment with Odoo DB settings for the startup script
        env = os.environ.copy()
        env["DB_NAME"] = config.get("db_name", "odoo")
        env["PGHOST"] = config.get("db_host", "localhost")
        _port = config.get("db_port")
        env["PGPORT"] = str(_port) if _port else "5432"
        env["PGUSER"] = config.get("db_user", "odoo")
        db_password = config.get("db_password")
        if db_password is not None:
            env["PGPASSWORD"] = db_password
        ipython_dir = lab_path / ".ipython"
        env["IPYTHONDIR"] = str(ipython_dir)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.output = result.stdout + result.stderr
            if result.returncode == 0:
                self.state = "success"
            else:
                self.state = "error"
        except FileNotFoundError:
            self.output = "papermill command not found."
            self.state = "error"
            return
        except Exception as e:
            _logger.error("Failed to run notebook %s: %s", self.name, e)
            self.output = str(e)
            self.state = "error"
            return

        return
