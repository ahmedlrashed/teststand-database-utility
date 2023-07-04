# ======================== Import libraries
import pathlib

import dash
import pandas as pd
from dash import dcc, Input, Output, html, dash_table
import base64
import io

import ts_db

# ======================== Generate dataset from ts_db.py script
"""Open TestStand database (.mdb) when user clicks { Download } button """

# ======================== Dash App
app = dash.Dash(__name__, prevent_initial_callbacks=True)
server = app.server

output_folder = r"C:\TestStand Results"
file_paths = []

for p in pathlib.Path(output_folder).glob("*.csv"):
    if p.is_file():
        file_paths.append(p.resolve().as_posix())

# ======================== App Layout
title = html.H1(
    "TestStand Database Utility",
    style={"text-align": "center", "background-color": "#ede9e8"},
)
upload = html.Div(
    dcc.Upload(
        id="upload-data",
        children=html.Div(
            ["Drag and Drop or ", html.A("Select TestStand .mdb File to Process")]
        ),
        style={
            "width": "95%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "3px",
            "borderStyle": "dashed",
            "borderRadius": "10px",
            "textAlign": "center",
            "margin": "20px",
        },
    ),
)
output_data = html.Div(id="output-data-upload")
dropdown = html.Div(
    dcc.Dropdown(
        id="dropdown_filename",
        options=[{"label": i, "value": i} for i in file_paths],
        # options=[],
        # value=None,
    )
)
data_log = html.Div(id="data_log")

app.layout = html.Div([title, upload, output_data, dropdown, data_log])


# ======================== App Callbacks/FileIO
@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
)
def import_contents(contents, filename):
    """Open TestStand database (.mdb) with user prompt"""
    if "mdb" in filename:
        # Only allow MS Access MDB file type

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        file_like_object = io.BytesIO(decoded)

        db_filepath = file_like_object
        print(filename)
        print(db_filepath)

        """Execute core python script to decompose the TestStand database file"""
        ts_db.main(db_filepath)

        children = [filename]
        return children


# ======================== App Callbacks/UI
# @app.callback(
#     [Output("dropdown", "options")],
#     [Input('upload-data', 'contents'),
#      Input('upload-data', 'filename')])
# )def update_options(contents, filename):
#     # ======================== Update dropdown menu options based on CSV files generated
#
#         lst = file_paths
#         return lst


@app.callback(
    [Output("data_log", "children")],
    [Input("dropdown_filename", "value")],
    prevent_initial_call=True,
)
def update_table(user_select):
    # ======================== Reading Selected csv file
    ts_table = pd.read_csv(user_select)
    return [dash_table.DataTable(id="data_tbl", data=ts_table.to_dict("records"))]


# ======================== Run  server
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
