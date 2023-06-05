# ======================== Import libraries
import pandas as pd
import pathlib
import dash
from dash import dcc, Input, Output, html, dash_table

# ======================== Generate dataset from ts_db.py script
import ts_db

ts_db.main()

# ======================== Dash App
app = dash.Dash(__name__)
server = app.server

# ======================== Generic Test Results directory (for universal reuse)
output_folder = r"C:\TestStand Results"

# Filter file name list for files ending with .csv
fileNames = []
filePaths = []
for p in pathlib.Path(output_folder).glob("*.csv"):
    if p.is_file():
        fileNames.append(p.name)
        filePaths.append(p.resolve().as_posix())

# ======================== App Layout
title = html.H1(
    "TestStand Data Log",
    style={"text-align": "center", "background-color": "#ede9e8"},
)
dropdown = html.Div(
    dcc.Dropdown(
        id="dropdown_filename",
        options=[{"label": i, "value": j} for i, j in zip(fileNames, filePaths)],
    )
)
data_log = html.Div(id="data_log")

app.layout = html.Div([title, dropdown, data_log])


@app.callback(
    [Output("data_log", "children")],
    [Input("dropdown_filename", "value")],
    prevent_initial_call=True,
)
def update_table(user_select):
    # ======================== Reading Selected csv file
    ts_table = pd.read_csv(user_select)
    return [dash_table.DataTable(id="data_tbl", data=ts_table.to_dict("records"))]


# -------------------------------------------------------------------------------------
# Run local server
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
