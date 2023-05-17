#!/usr/bin/env python
# coding: utf-8
"""
Database querying, extracting, and processing.
"""


def connect_odbc(db_filename):
    """Connect to database located at input filename"""

    import pyodbc

    # The DRIVER curly brackets are doubled up to escape themselves
    # The DBQ curly brackets are NOT doubled up because they are placeholders
    con_string = (
        "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};" "DBQ={};"
    ).format(db_filename)

    cnxn = pyodbc.connect(con_string)
    crsr = cnxn.cursor()

    return crsr


def query_seq_calls(crsr):
    """Query Step_SeqCalls Table"""

    sql_string2 = """
    SELECT STEP_SEQCALL.STEP_RESULT, STEP_SEQCALL.SEQUENCE_FILE_PATH 
    FROM STEP_SEQCALL
    ORDER BY STEP_SEQCALL.STEP_RESULT ASC
    """

    crsr.execute(sql_string2)
    sequence_calls = crsr.fetchall()

    return sequence_calls


def create_sequence_list(sequence_calls):
    """Create list of tuples (x,y) mapping x = Step_Parent to y = Sequence_Name"""

    from pathlib import Path

    seq_list = []

    for sequence in sequence_calls:

        # Update raw filepaths to final table names
        sequence[1] = "Test Data " + Path(sequence[1]).stem

        # Create list containing each unique sequence in the .mdb table
        while sequence[1] not in seq_list:
            seq_list.append(sequence[1])

    return seq_list


def create_table_dict(seq_list):
    """Query Step_SeqCalls Table"""

    tbl_dict = {}

    # Assign seq_list entries as keys with empty array as each entry's value (to be populated)
    for seq_name in seq_list:
        tbl_dict[f"{seq_name}"] = []

    return tbl_dict


def query_uut_runs(crsr):
    """Query UUT_Results Table"""

    from tkinter import simpledialog

    # Get all desired test runs filtered by start-date and optional user-name
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
        sql_string += " WHERE START_DATE_TIME >= #{}#".format(start_date)

    if user_name:
        sql_string += " AND USER_LOGIN_NAME = '{}'".format(user_name)

    sql_string += " ORDER BY START_DATE_TIME, TEST_SOCKET_INDEX"

    crsr.execute(sql_string)
    uut_runs = crsr.fetchall()

    return uut_runs


def generate_test_table(crsr, uut_runs, tbl_dict, sequence_calls):
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
                key_name = (
                    f"{step.STEP_NAME} ({step.UNITS}) {limit_info} [{repeat_index}]"
                )

                # Append numeric suffix to distinguish.
                while key_name in data:
                    repeat_index += 1
                    key_name = (
                        f"{step.STEP_NAME} ({step.UNITS}) {limit_info} [{repeat_index}]"
                    )

                # Add new key-value pair with precision of 3 decimal places
                data[key_name] = round(val, 3)

        # Convert STEP_PARENT index to the corresponding sequence file dictionary value
        dict_val = ""
        for x, y in sequence_calls:
            if x == step.STEP_PARENT:
                dict_val = y

        # Append data to the appropriate output table according to dictionary value
        tbl_dict[f"{dict_val}"].append(data)

    # print("---- Test Data generated ----")
