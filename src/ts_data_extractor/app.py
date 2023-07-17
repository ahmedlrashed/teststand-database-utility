"""
USE CASE :: This is the top-level web application implementation of the python script.
            Uses custom file_io and database modules.
            Calls the submodule ts_db.py script.
"""

# importing the required libraries
import pathlib
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import ts_db

# Initialize the flask app
app = Flask(__name__)

# get the current working directory
current_working_directory = Path.cwd()

# print output to the console
print(current_working_directory)

# Create the upload folder
upload_folder = Path(current_working_directory).joinpath("uploads")
if not Path.exists(upload_folder):
    Path.mkdir(upload_folder)

# Set maximum size of the file
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# Configure the upload folder
app.config["UPLOAD_FOLDER"] = upload_folder

# Configure the allowed extensions
allowed_extensions = ["mdb"]


def check_file_extension(filename):
    return filename.split(".")[-1] in allowed_extensions


# Start page for web app
@app.route("/")
def index():
    return render_template("upload.html")


# Result page after user selects file to upload
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":  # check if the method is post
        f = request.files["file"]  # get the file from the files object

        # Saving the file in the required destination
        if check_file_extension(f.filename):
            db_filepath = Path.joinpath(
                app.config["UPLOAD_FOLDER"], secure_filename(f.filename)
            )
            f.save(db_filepath)  # this will secure the file

            # =================================================================== #
            # Execute core python script to decompose the TestStand database file #
            # =================================================================== #
            csv_file_count = ts_db.main(db_filepath)

            # Purge contents of uploads folder after script is finished
            for file in Path.iterdir(upload_folder):
                Path.unlink(Path.joinpath(upload_folder, file))

            return f"MDB has been processed:: {csv_file_count} CSV files exported to C:\\TestStand Results"

        else:
            return "The file extension is not allowed"


# After core python script runs, display exported CSV files in dropdown menu and table
output_folder = r"C:\TestStand Results"
file_paths = []

for p in pathlib.Path(output_folder).glob("*.csv"):
    if p.is_file():
        file_paths.append(p.resolve().as_posix())

#
# def update_table(user_select):
#     ts_table = pd.read_csv(user_select)


if __name__ == "__main__":
    app.run()  # running the flask app
