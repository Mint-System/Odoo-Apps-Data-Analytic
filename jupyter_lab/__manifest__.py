# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Jupyter Lab",
    "summary": """
        Manage Jupyter Lab projects and access Odoo ORM from notebooks.
    """,
    "author": "Mint System GmbH",
    "website": "https://www.mint-system.ch/",
    "category": "Repository",
    "development_status": "Production/Stable",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "views/jupyter_lab_views.xml",
        "views/jupyter_notebook_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["images/screen.png"],
    "assets": {
        "web.assets_backend": [
            "jupyter_lab/static/src/css/style.css",
        ],
    },
    "demo": ["demo/demo.xml"],
    "external_dependencies": {"python": ["jupyter"]},
}
