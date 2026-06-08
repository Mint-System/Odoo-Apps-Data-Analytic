# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Jupyter Notebook Run",
    "summary": """
        Run parameterized Jupyter notebooks from Odoo.
    """,
    "author": "Mint System GmbH",
    "website": "https://www.mint-system.ch/",
    "category": "Repository",
    "development_status": "Production/Stable",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["jupyter_lab"],
    "data": [
        "security/ir.model.access.csv",
        "views/jupyter_notebook_run_views.xml",
        "wizard/jupyter_notebook_run_wizard_views.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["images/screen.png"],
    "external_dependencies": {"python": ["papermill", "pandas"]},
}
