# Purpose
Tool to help extract and analyze test data from the default TestStand database.

TestStand has a native database logger that stores test runs in a local database using the default TestStand schema. There are Pro and Cons to this approach. For example, using the default schema allows for a one-click data recording solution that records *all* test data and limits. It also has the flexibility to change with the test - new steps and limits can be added or existing steps and limits changed without changing the schema or losing test history.

However, extracting the data for analysis is more cumbersome than just exporting a simple table - unique IDs need to be matched across tables and data needs to be groomed. This extraction and analysis is the main purpose of these sets of tools.

NOTE: Use the Test Reports when looking at data for a small number of tests - they are already formatted for viewing.

# Prerequisites
NOTE: Python packages can be installed with `pip -r requirements.txt`

* [Python 3.7+](www.python.org)
* [JupyterLab](jupyter.org) Only needed for original jupyter notebook
* [pyodbc](https://github.com/mkleehammer/pyodbc)
* [pandas](pandas.pydata.org)
