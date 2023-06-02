# Purpose
Tool to help extract and analyze test data from the default TestStand database.

TestStand has a native database logger that stores test runs in a local database using the default TestStand schema. There are Pro and Cons to this approach. For example, using the default schema allows for a one-click data recording solution that records *all* test data and limits. It also has the flexibility to change with the test - new steps and limits can be added or existing steps and limits changed without changing the schema or losing test history.

However, extracting the data for analysis is more cumbersome than just exporting a simple table - unique IDs need to be matched across tables and data needs to be groomed. This extraction and analysis is the main purpose of these sets of tools.

NOTE: Use the Test Reports when looking at data for a small number of tests - they are already formatted for viewing.

# Prerequisites
NOTE: Python packages should be installed with `poetry install` command for current pyproject.toml

[tool.poetry.dependencies]
python = "^3.10"
pyodbc = "^4.0.35"
pandas = "^2.0.0"
isort = "^5.12.0"
dash = "^2.9.3"
requests = "^2.28.2"
