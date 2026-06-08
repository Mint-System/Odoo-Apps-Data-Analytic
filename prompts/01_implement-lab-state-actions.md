---
title: "Implement lab state actions"
state: completed
---

# Run 01

Note: @Clanker refers to the "ai agent" (you) who is working on this task.

@Clanker when working on this task, make sure to:

- Read context and task section first
- Prepare a list of todos
- Update the todo list while working on the task

## Context

Read the `AGENTS.md` and `README.md` to get an understanding of the project.

## Task

I want you to implement the action methods in
`addons/data_analytic/jupyter_lab/models/jupyter_lab.py` according to these transitions
and states:

- draft: Initial state, name can be edited and path value is generated.
- draft -[init]-> ready: The init action creates the folder, generates the token and
  adds a default `main.ipynb`.
- ready -[start]-> running: The start action launches the web app. If start fails the
  lab stays in ready state.
- running -[stop]-> ready: Kills the jupyter lab process.

For the initialization of the project have a look at `bin/init-odoo-jupyter`. The
`bin/start-odoo-jupyter` has details on how the process can be started and detached.
Instead of reading db credentials from env vars, they are passed from the Odoo config.
The uid must be the user that is executing the start action.

The templated `main.ipynb` shall be stored as an actual file in
`addons/data_analytic/jupyter_lab/static/templates/main.py`. Same goes for the
`00-odoo.py` startup template.

## Worklog

@Clanker Add a summary here once the task has been completed.

- Created static template files `main.ipynb` and `00-odoo.py` in
  `addons/data_analytic/jupyter_lab/static/templates/`.
- Implemented `_init_jupyter_lab` to create the lab directory, generate jupyter config,
  copy template files (including `main.ipynb` and the startup script).
- Implemented `action_initialize` to transition from `draft` to `ready`.
- Implemented `action_start` to launch `jupyter-lab` in a detached subprocess using
  `subprocess.Popen` with `start_new_session=True`. It reads database credentials from
  Odoo config (`odoo.tools.config`) instead of environment variables, passes the current
  Odoo user's `uid` via `ODOO_UID` environment variable to the startup script, enforces
  that no other lab is running, and transitions state to `running` while storing the
  process PID. Failures keep the lab in `ready` state by raising `UserError` before the
  state change.
- Implemented `action_stop` to terminate the stored PID with `SIGTERM` and transition
  back to `ready`.
- Updated `00-odoo.py` template to read `uid` from `ODOO_UID` environment variable.

## Fixes

- Changed `token` field from unstable `compute`+`store` to a stable `default` Char field
  so the token is generated once on record creation and persists across state changes,
  avoiding token mismatches between the started Jupyter server and the Odoo UI.
- Fixed `00-odoo.py` startup script to be more robust: it no longer crashes the kernel
  when `DB_NAME` is missing or the database is temporarily unreachable. It defensively
  reads environment variables, logs any traceback, and keeps the kernel alive so the
  user can see diagnostics.
- Fixed `action_start` to pass the Odoo source directory into `PYTHONPATH`, ensuring
  spawned Jupyter kernels can import `odoo` even when they run in a different Python
  context.
- Added an immediate health-check to `action_start` that verifies the `jupyter-lab`
  process didn't exit right after launch (e.g., due to port conflicts or missing
  config). If it did, a `UserError` is raised with a snippet of the log so the failure
  is visible and the lab stays in `ready` state.
- Added missing `@api.depends` decorators to compute methods (`url`, `local_path`,
  `log_file`, `log_content`) for proper cache invalidation in Odoo 18.

@Clanker Set frontmatter state to completed.
