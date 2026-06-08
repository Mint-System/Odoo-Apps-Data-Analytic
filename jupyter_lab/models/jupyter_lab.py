# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import secrets
import shutil
import signal
import subprocess
from pathlib import Path

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tools import config

_logger = logging.getLogger(__name__)


class JupyterLab(models.Model):
    _name = "jupyter.lab"
    _description = "Jupyter Lab"

    name = fields.Char()
    local_path = fields.Char(compute="_compute_local_path")
    url = fields.Char(compute="_compute_url")
    pid = fields.Integer(readonly=True)
    token = fields.Char(default=lambda self: secrets.token_hex(16), readonly=True)
    log_file = fields.Char(compute="_compute_log_file")
    log_content = fields.Text(compute="_compute_log_content")
    notebook_ids = fields.One2many("jupyter.notebook", "lab_id", string="Notebooks")
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

    @api.depends("token")
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

    @api.depends("name")
    def _compute_local_path(self):
        slugify = self.env["ir.http"]._slugify
        for lab in self:
            lab.local_path = Path(config["data_dir"]) / "jupyter_lab" / slugify(lab.name)

    @api.depends("local_path")
    def _compute_log_file(self):
        for lab in self:
            lab.log_file = str(Path(lab.local_path) / "jupyter_lab.log")

    @api.depends("log_file")
    def _compute_log_content(self):
        for lab in self:
            log_path = Path(lab.log_file)
            if log_path.exists():
                try:
                    with open(log_path, encoding="utf-8", errors="replace") as f:
                        lab.log_content = f.read()
                except OSError:
                    lab.log_content = ""
            else:
                lab.log_content = ""

    def _init_jupyter_lab(self):
        """
        Create juypter lab directory and config file.
        Copy startup script and main.ipynb template.
        """
        self.ensure_one()
        path = Path(self.local_path)
        path.mkdir(parents=True, exist_ok=True)

        ipython_dir = path / ".ipython"
        startup_dir = ipython_dir / "profile_default" / "startup"
        startup_dir.mkdir(parents=True, exist_ok=True)

        templates_dir = Path(get_module_resource("jupyter_lab", "static/templates"))
        shutil.copy(templates_dir / "main.ipynb", path / "main.ipynb")
        shutil.copy(templates_dir / "00-odoo.py", startup_dir / "00-odoo.py")

        env = os.environ.copy()
        env["JUPYTER_CONFIG_DIR"] = str(path / ".jupyter")
        try:
            subprocess.run(
                ["jupyter", "lab", "--generate-config"],
                env=env,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            _logger.warning("Could not generate jupyter config for %s", self.name)

    def action_initialize(self):
        """
        Initialize jupyter lab directory and set state to ready.
        """
        self.ensure_one()
        self._init_jupyter_lab()
        existing = self.env["jupyter.notebook"].search([("name", "=", "main.ipynb"), ("lab_id", "=", self.id)], limit=1)
        if not existing:
            self.env["jupyter.notebook"].create(
                {
                    "name": "main.ipynb",
                    "lab_id": self.id,
                }
            )
        self.state = "ready"
        return

    def action_refresh_log(self):
        """
        Refresh log content.
        """
        self._compute_log_content()
        return

    def action_start(self):
        """
        Launch jupyter lab in directory. Ensure no other juypter lab is running.
        Pass current user uid to startup script. Redirect output to log file.
        """
        self.ensure_one()

        if self.state != "ready":
            raise UserError(_("Lab must be in ready state to start."))

        running_labs = self.search([("state", "=", "running"), ("id", "!=", self.id)])
        if running_labs:
            raise UserError(_("Another Jupyter Lab is already running. Stop it before starting a new one."))

        if not shutil.which("jupyter-lab"):
            raise UserError(_("jupyter-lab command not found in PATH."))

        notebook_dir = Path(self.local_path).resolve()
        ipython_dir = notebook_dir / ".ipython"
        config_dir = notebook_dir / ".jupyter"

        env = os.environ.copy()
        db_name = config.get("db_name", "odoo")
        env["DB_NAME"] = db_name
        env["PGHOST"] = config.get("db_host", "localhost")
        _port = config.get("db_port")
        env["PGPORT"] = str(_port) if _port else "5432"
        env["PGUSER"] = config.get("db_user", "odoo")
        db_password = config.get("db_password")
        if db_password is not None:
            env["PGPASSWORD"] = db_password
        env["ODOO_UID"] = str(self.env.uid)
        env["IPYTHONDIR"] = str(ipython_dir)
        env["JUPYTER_CONFIG_DIR"] = str(config_dir)

        cmd = [
            "jupyter-lab",
            f"--ServerApp.root_dir={notebook_dir}",
            f"--ServerApp.token={self.token}",
            "--ServerApp.open_browser=False",
            "--ServerApp.ip=0.0.0.0",
            "--ServerApp.port=8888",
            "--allow-root",
        ]

        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = open(log_path, "w", encoding="utf-8")

        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except Exception as e:
            log_handle.close()
            _logger.error(_("Failed to start jupyter lab: %s", e))
            raise UserError(_("Failed to start jupyter lab: %s", e))

        log_handle.close()

        self.pid = process.pid
        self.state = "running"
        return

    def action_open(self):
        """
        Open Jupyter Lab in a new browser tab.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.url,
            "target": "new",
        }

    def action_stop(self):
        """
        Stop juypter lab process.
        """
        self.ensure_one()

        if self.state != "running":
            raise UserError(_("Lab is not running."))

        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                _logger.warning(_("Process %s not found, already terminated.", self.pid))
            except Exception as e:
                _logger.error(_("Failed to stop process %s: %s", self.pid, e))
                raise UserError(_("Failed to stop process: %s", e))

        self.pid = 0
        self.state = "ready"
        return

    def action_reset(self):
        """
        Reset lab back to draft: stop process, delete generated config, and remove notebook records.
        """
        self.ensure_one()

        if self.state == "running":
            self.action_stop()

        path = Path(self.local_path)
        if path.exists():
            # Remove generated directories and log, keep .ipynb files.
            shutil.rmtree(path / ".jupyter", ignore_errors=True)
            shutil.rmtree(path / ".ipython", ignore_errors=True)
            try:
                Path(self.log_file).unlink()
            except OSError:
                _logger.warning("Could not delete log file %s", self.log_file, exc_info=True)

        self.notebook_ids.unlink()

        self.write({"state": "draft", "pid": 0})
        return
