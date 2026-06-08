"""
Odoo IPython startup script.

This script is sourced automatically by IPython when the Jupyter kernel starts.
It pushes odoo, env, cr, uid, self, and api into the notebook namespace.
"""

import atexit
import os

import odoo
from odoo import api
from odoo.modules.registry import Registry
from odoo.tools import config

db_name = os.environ["DB_NAME"]
config["db_name"] = db_name
config["db_host"] = os.environ.get("PGHOST", "localhost")
config["db_port"] = os.environ.get("PGPORT", "5432")
config["db_user"] = os.environ.get("PGUSER", "odoo")
config["db_password"] = os.environ.get("PGPASSWORD", "odoo")

registry = Registry(db_name)
cr = registry.cursor()
uid = int(os.environ.get("ODOO_UID", 2))
ctx = api.Environment(cr, uid, {})["res.users"].context_get()
env = api.Environment(cr, uid, ctx)
self = env.user

ip = get_ipython()  # noqa: F821
ip.push(
    {
        "odoo": odoo,
        "env": env,
        "cr": cr,
        "uid": uid,
        "self": self,
        "api": api,
    }
)


@atexit.register
def _cleanup():
    if cr is not None:
        try:
            cr.rollback()
            cr.close()
        except Exception:
            log.exception("Error during cursor cleanup")
