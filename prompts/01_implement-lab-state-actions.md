---
title: "Implement lab state actions"
state: ready
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

I want you to implement the action methods in `addons/data_analytic/jupyter_lab/models/jupyter_lab.py` according to these transitions and states:

- draft: Initial state, name can be edited and path value is generated.
- draft -[init]-> ready: The init action creates the folder, generates the token and adds a default `main.ipynb`.
- ready -[start]-> running: The start action launches the web app. If start fails the lab stays in ready state.
- running -[stop]-> ready: Kills the jupyter lab process.

For the initialization of the project have a look at `bin/init-odoo-jupyter`. The `bin/start-odoo-jupyter` has details on how the process can be started and detached. Instead of reading db credentials from env vars, they are passed from the Odoo config. The uid must be the user that is executing the start action.

The templated `main.ipynb` shall be stored as an actual file in `addons/data_analytic/jupyter_lab/static/templates/main.py`. Same goes for the `00-odoo.py` startup template.

## Worklog

@Clanker Add a summary here once the task has been completed.

@Clanker Set frontmatter state to completed.
