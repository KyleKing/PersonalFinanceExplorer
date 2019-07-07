"""DoIt Script. Run with `poetry run doit` or `poetry run doit run exportReq`."""

from dash_charts.dodoBase import task_exportReq, task_updateCL  # noqa: F401

# Create list of all tasks run with `poetry run doit`
DOIT_CONFIG = {'default_tasks': [
    'exportReq', 'updateCL',
]}
