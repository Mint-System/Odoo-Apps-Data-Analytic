---
title: "Create jupyter notebook run"
state: completed
---

# Run 02

Note: @Clanker refers to the "ai agent" (you) who is working on this task.

@Clanker when working on this task, make sure to:

- Read context and task section first
- Prepare a list of todos
- Update the todo list while working on the task

## Context

Read the `AGENTS.md` and `README.md` to get an understanding of the project.

## Task

I have initialized a new module module `addons/data_analytic/jupyter_notebook_run`.
Please complete the module according to the following specifications:

This module adds a model `jupyter.notebook.run` with name, notebook_id, state, output,
attachment_id, values and lab_id (related). From the `jupyter.notebook` the run wizard
can be opened. This wizard (`jupyter.notebook.run.wizard`) allows creating and
parameterizing a run with variables (values) and an attachment.

With a click on "Run" in the wizard form the run is created and immediately executed.
From the run form a completed run can be reset to `draft` and then re-run.

The state of the run is as follows:

- draft (default)
- running
- success
- error

Attachment files are copied to the lab folder and the papermill command is called to run
the notebook. The papermill output is captured and stored in the run output. Runs can
only be created via the wizard; manual creation and deletion from the list/form views
are disabled.

Details on how to run a notebook with papermill are available in
`bin/run-jupyter-notebook`. Ensure that the output overwrites the input notebook.

To create the model use `task generate-module-model` and to create the views use
`task generate-module-view`. Generate access rules with `task generate-module-security`.

## Worklog

@Clanker Add a summary here once the task has been completed.

@Clanker Set frontmatter state to completed.

- Created `jupyter.notebook.run` model with fields: name, notebook_id, state
  (draft/running/success/error), output (text), attachment_id, values (JSON parameters),
  and lab_id (related to notebook_id.lab_id).
- Added `action_run()` method that validates the run is in `draft` before executing
  Papermill, copies attachment to the lab folder, builds the command with JSON
  parameters, captures stdout/stderr into the run output, and updates state to `success`
  or `error`.
- Added `action_reset()` method to clear output and return a run to `draft` state so it
  can be re-executed.
- Created `jupyter.notebook.run.wizard` transient model for parameterizing runs with
  attachment and values. The wizard creates the run and immediately executes it via
  `action_run()`, then opens the run form.
- Added `action_open_run_wizard` method on `jupyter.notebook` to open the wizard with
  the notebook pre-filled.
- Created list, form, and search views for `jupyter.notebook.run`, plus a menu item
  directly under the `Jupyter` root menu.
- Fixed menu hierarchy: removed duplicate `Jupyter` submenu so `Runs`, `Notebooks`, and
  `Labs` all appear directly under the `Jupyter` root menu (ordered Runs | Notebooks |
  Labs).
- Created wizard form view and inherited the notebook form view to add a "Run" button
  that opens the wizard.
- Added `Run` and `Reset` buttons to the run form; `Run` is visible only in `draft`,
  `Reset` only in `success` or `error`.
- Disabled direct creation and deletion on the run list and form views
  (`create="false"`, `delete="false"`) so runs can only be created via the wizard.
- Added `security/ir.model.access.csv` with access rules for the new models.
- Updated `__manifest__.py` to include data files and added `demo/demo.xml`.
- Created demo data: a `jupyter.notebook` record and a `jupyter.notebook.run` record in
  `draft` state linked to it.
- Verified all Python and XML files compile and are well-formed.
