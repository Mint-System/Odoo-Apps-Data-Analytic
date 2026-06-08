Test Instructions for Jupyter Notebook Run
==========================================

Purpose
-------
Verify that a notebook run can read an uploaded CSV attachment and process it with passed parameters.

Prerequisites
-------------
- The ``jupyter_lab`` module is installed and a lab is initialized.
- The ``jupyter_notebook_run`` module is installed.

Steps
-----

#. **Initialize a Jupyter Lab**

   - Open *Jupyter > Labs* and create a new lab.
   - Click **Initialize** to set the lab directory and generate ``main.ipynb``.

#. **Update the ``main.ipynb`` template**

   The default template only prints ``env.user.name``. Add a new cell that reads the uploaded ``input.csv`` file and applies the ``foo`` parameter.

   Insert the following code cell **after** the *Papermill parameters* cell::

      import pandas as pd
      import os

      # The input.csv attachment is copied to the lab folder by the run wizard
      csv_path = os.path.join(os.getcwd(), "input.csv")

      df = pd.read_csv(csv_path)
      df.head()

   Optional: add another cell to use the ``foo`` parameter::

      # This value is injected by papermill at runtime
      print("parameter foo =", foo)

   Save the notebook.

#. **Prepare the run**

   - Go to *Jupyter > Notebooks* and open ``main.ipynb``.
   - Click the **Run** button on the notebook form. This opens the run wizard.

#. **Configure the run in the wizard**

   - **Attachment**: upload or select ``addons/data_analytic/jupyter_notebook_run/tests/input.csv``.
   - **Values** (JSON): ``{"foo": "bar"}``
   - Click **Run** to create and execute the run record.

#. **Verify the result**

   - The run form opens automatically.
   - Refresh the form or wait for the state to change from *Running* to *Success*.
   - In the **Output** panel you should see:

     - The ``input.csv`` being read via ``pandas``.
     - The printed ``foo`` parameter value (``bar``).
   - If the state is *Error*, the **Output** panel contains the full traceback for debugging.

Expected Output Snippet
-----------------------
A successful run should show something like::

   parameter foo = bar
   <DataFrame output showing the first rows of input.csv>

Troubleshooting
---------------

- **FileNotFoundError for ``input.csv``**: verify that the attachment was uploaded in the wizard and that the lab path matches the working directory used by papermill.
- **Pandas is not installed**: install it in the Python environment that runs papermill (``pip install pandas`` inside the same venv as Odoo).
- **Unknown parameter ``foo``**: ensure the *Papermill parameters* cell in the notebook declares ``foo = None`` (already present in the default template).
