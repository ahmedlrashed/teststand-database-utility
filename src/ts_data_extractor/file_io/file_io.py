#!/usr/bin/env python
# coding: utf-8
"""
File import and results output.
"""


def import_source():
    """Open TestStand database (.mdb) with user prompt"""

    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    # Prevent the root window from appearing
    Tk().withdraw()

    # Show an "Open" dialog box and return the path to the selected file
    db_filename = askopenfilename(
        title="Select TestStand Database File to Open",
        filetypes=(("MS Access", "*.mdb"), ("MS Access", "*.accdb")),
    )

    return db_filename


def export_results(seq_list, tbl_dict):
    """Export each output table to CSV file"""

    import pandas as pd
    from pathlib import Path

    output_folder = str(Path.cwd().parent.parent) + r"\results"

    for seq_name in seq_list:
        filename = seq_name + ".csv"
        output_file = output_folder + "\\" + filename
        filepath = Path(output_file)
        if filepath.is_file():
            write_header = False
        else:
            write_header = True
        pd.DataFrame.from_records(tbl_dict[f"{seq_name}"]).to_csv(
            output_file, mode="a", index=False, header=write_header
        )
        # print(f"---- {seq_name} exported ----")


def export_data_tables(seq_list, tbl_dict):
    """Export each output table as a dataframe to GUI panel"""

    import pandas as pd

    for seq_name in seq_list:
        pd.DataFrame.from_records(tbl_dict[f"{seq_name}"])
