#!/usr/bin/env python
# coding: utf-8
"""
Purpose
Extract data from default TestStand database using default Access NI schema. 
Data is converted to CSVs for import into another tool such as Minitab or analyzed in web app.

One CSV file will be created for each Sequence File name that was called - 
* Numeric Data - data of steps with Numeric Limit Tests; column names step names and tolerances

It is assumed that the entirety of the queried data has the same basic test structure
- step names, tolerances, and step sequences order is not drastically changing.
Changes to this will require normalization.
"""

import pandas as pd
import pyodbc
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
from pathlib import Path

# ------------------------------------------------------------------------------
"""Open database with user prompt"""

# Prevent the root window from appearing
Tk().withdraw()

# Show an "Open" dialog box and return the path to the selected file
db_filename = askopenfilename(
    title="Select TestStand Database File to Open",
    filetypes=(("MS Access", "*.mdb"), ("MS Access", "*.accdb")),
)

# ------------------------------------------------------------------------------
"""Connect to database located at input filename"""

con_string = "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};" "DBQ={};".format(
    db_filename
)

# Connect to database
cnxn = pyodbc.connect(con_string)
crsr = cnxn.cursor()

# ------------------------------------------------------------------------------
"""Query Step_SeqCalls Table"""

sql_string2 = """
SELECT STEP_SEQCALL.STEP_RESULT, STEP_SEQCALL.SEQUENCE_FILE_PATH 
FROM STEP_SEQCALL
ORDER BY STEP_SEQCALL.STEP_RESULT ASC
"""

crsr.execute(sql_string2)
sequence_calls = crsr.fetchall()

# Declaration of empty dictionary for dynamic output tables
tbl_dict = {}

# Declaration of empty sequence list
seq_list = []

# Create look-up table mapping x = Step_Parent to y = Sequence_Name as Tuple (x,y)
for sequence in sequence_calls:

    # Update raw filepaths to final table names
    sequence[1] = "Test Data " + Path(sequence[1]).stem

    # Create list containing each unique sequence in the .mdb file
    while sequence[1] not in seq_list:
        seq_list.append(sequence[1])

    # Assign list entries as keys with empty array as each entry's value (will populate in next section)
    for seq_name in seq_list:
        tbl_dict[f"{seq_name}"] = []


# ------------------------------------------------------------------------------
"""Query UUT_RESULT Table"""

start_date = simpledialog.askstring(
    "OPTIONAL FILTER",
    "Enter start-date filter with format\nYYYY-MM-DD HH:mm\n(leave blank to get all dates) ::",
)
user_name = simpledialog.askstring(
    "OPTIONAL FILTER", "Enter user-name filter\n(leave blank to get all users) ::"
)

sql_string = (
    "SELECT ID, STATION_ID, START_DATE_TIME, EXECUTION_TIME, TEST_SOCKET_INDEX, UUT_SERIAL_NUMBER, UUT_STATUS "
    "FROM UUT_RESULT "
    "WHERE UUT_STATUS <> 'Terminated' and STATION_ID is not NULL"
)

if start_date:
    sql_string += " AND START_DATE_TIME >= #{}#".format(start_date)

if user_name:
    sql_string += " AND USER_LOGIN_NAME = '{}'".format(user_name)

sql_string += " ORDER BY START_DATE_TIME, TEST_SOCKET_INDEX"

crsr.execute(sql_string)
uut_runs = crsr.fetchall()


# ------------------------------------------------------------------------------
"""Construct Test Results Data Table"""

for run in uut_runs:

    # Identifying Metadata for each Test Run
    data = {
        "Test Start": run.START_DATE_TIME,
        "Station ID": run.STATION_ID,
        "Serial Number": run.UUT_SERIAL_NUMBER,
        "Test Socket": run.TEST_SOCKET_INDEX,
        "Test Status": run.UUT_STATUS,
        "Test Time (s)": round(run.EXECUTION_TIME, None),
    }

    # Query individual step results inside each Test Run
    crsr.execute(
        f"""
    SELECT  STEP_RESULT.ID, 
            STEP_RESULT.STEP_PARENT, 
            STEP_RESULT.STEP_NAME, 
            STEP_RESULT.STEP_TYPE, 
            STEP_RESULT.STATUS, 
            STEP_RESULT.ORDER_NUMBER,
            PROP_RESULT.ID AS PROP_ID, 
            PROP_RESULT.TYPE_NAME, 
            PROP_RESULT.DATA, 
            PROP_RESULT.NAME,
            PROP_NUMERICLIMIT.COMP_OPERATOR AS COP, 
            PROP_NUMERICLIMIT.HIGH_LIMIT AS HL, 
            PROP_NUMERICLIMIT.LOW_LIMIT AS LL, 
            PROP_NUMERICLIMIT.UNITS AS UNITS
    FROM (STEP_RESULT LEFT JOIN PROP_RESULT ON STEP_RESULT.ID = PROP_RESULT.STEP_RESULT)
         LEFT JOIN PROP_NUMERICLIMIT ON PROP_RESULT.ID = PROP_NUMERICLIMIT.PROP_RESULT
    WHERE STEP_RESULT.UUT_RESULT = {run.ID} 
         and STEP_RESULT.STEP_TYPE = 'NumericLimitTest' 
         and PROP_RESULT.TYPE_NAME = 'NumericLimitTest'
    ORDER BY STEP_RESULT.ORDER_NUMBER ASC
    """
    )
    run_steps = crsr.fetchall()

    # Extract, construct, and append Test Data values to key-defined Test Data Tables
    for step in run_steps:

        # Convert data to Python types
        val = None
        if step.TYPE_NAME == "Boolean":
            val = bool(step.DATA)

        elif step.TYPE_NAME == "Number" or step.TYPE_NAME == "NumericLimitTest":
            val = float(step.DATA)

        # Extract desired data
        if (
            step.STEP_TYPE == "NumericLimitTest"
            and step.STATUS != "Skipped"
            and val is not None
        ):
            # Construct limit info string based on comparison type
            limit_info = ""
            if step.COP == "LT":
                limit_info = f"< {step.LL}"
            elif step.COP == "LE":
                limit_info = f"<= {step.LL}"
            elif step.COP == "GT":
                limit_info = f"> {step.LL}"
            elif step.COP == "GE":
                limit_info = f">= {step.LL}"
            elif step.COP == "GTLT":
                limit_info = f"{step.LL} < x < {step.HL}"
            elif step.COP == "GELE":
                limit_info = f"{step.LL} <= x <= {step.HL}"
            elif step.COP == "EQT":
                limit_info = f"{step.LL} <= x <= {step.HL}"
            elif step.COP == "EQ":
                limit_info = f" == {step.LL}"
            else:
                break

            # Different step runs will have repeated step name.
            repeat_index = 0
            key_name = f"{step.STEP_NAME} ({step.UNITS}) {limit_info} [{repeat_index}]"

            # Append numeric suffix to distinguish.
            while key_name in data:
                repeat_index += 1
                key_name = (
                    f"{step.STEP_NAME} ({step.UNITS}) {limit_info} [{repeat_index}]"
                )

            # Add new key-value pair with precision of 3 decimal places
            data[key_name] = round(val, 3)

            # output_folder = str(Path.cwd().parent.parent) + r"\raw"
            # filename = f"{step.STEP_NAME}" + ".csv"
            # output_file = output_folder + "\\" + filename
            # pd.DataFrame.from_records(data).to_csv(output_file, index=False)

    # Convert STEP_PARENT index to the corresponding sequence file dictionary value
    dict_val = ""
    for x, y in sequence_calls:
        if x == step.STEP_PARENT:
            dict_val = y
            # print(x, y)

    # Append data to the appropriate output table according to dictionary value
    tbl_dict[f"{dict_val}"].append(data)

print("---- Test Data generated ----")


# ------------------------------------------------------------------------------
"""Export each output table to CSV file"""

output_folder = str(Path.cwd().parent.parent) + r"\results"

for seq_name in seq_list:
    filename = seq_name + ".csv"
    output_file = output_folder + "\\" + filename
    filepath = Path(output_file)
    if filepath.is_file():
        show_header = False
    else:
        show_header = True
    pd.DataFrame.from_records(tbl_dict[f"{seq_name}"]).to_csv(
        output_file, mode="a", index=False, header=show_header
    )
    print(f"---- {seq_name} exported ----")
