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

from database import *
from file_io import *


def main(db_filename):
    """Execute core python script to decompose input TestStand database file <db_filename>"""

    # Connect, clean, and extract dataset passed in as parameter
    crsr = connect_odbc(db_filename)
    sequence_calls = query_seq_calls(crsr)
    seq_list = create_sequence_list(sequence_calls)
    tbl_dict = create_table_dict(seq_list)
    uut_runs = query_uut_runs(crsr)

    # Generate test results table by sequence name (save to memory)
    generate_test_table(crsr, uut_runs, tbl_dict, sequence_calls)

    # Export test results in memory to CSV files and return csv_file_count
    return export_results(seq_list, tbl_dict)


if __name__ == "__main__":
    main()
