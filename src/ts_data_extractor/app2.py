# Import libraries
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import run
import pathlib
from pathlib import Path

# Generate the dataset
if __name__ == "__main__":
    # run.py executed as script
    run.main()

# Load the dataset
# output_folder = str(Path.cwd().parent.parent) + r"\results"
# df_list = []
# for p in pathlib.Path(output_folder).glob("*.csv"):
#     if p.is_file():
#         df_list.append(p)

for seq_name in seq_list:

    pd.DataFrame.from_records(tbl_dict[f"{seq_name}"])

# Create the Dash app
app = Dash()

# Set up the app layout
geo_dropdown = dcc.Dropdown(options=avocado["geography"].unique(), value="New York")

app.layout = html.Div(
    children=[
        html.H1(children="Avocado Prices Dashboard"),
        geo_dropdown,
        dcc.Graph(id="price-graph"),
    ]
)


# Set up the callback function
@app.callback(
    Output(component_id="price-graph", component_property="figure"),
    Input(component_id=geo_dropdown, component_property="value"),
)
def update_graph(selected_geography):
    filtered_avocado = avocado[avocado["geography"] == selected_geography]
    line_fig = px.line(
        filtered_avocado,
        x="date",
        y="average_price",
        color="type",
        title=f"Avocado Prices in {selected_geography}",
    )
    return line_fig


# Run local server
if __name__ == "__main__":
    app.run_server(debug=True)
