# importing the required libraries
import os
import pathlib

import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import ts_db

# Initialize the flask app
app = Flask(__name__)

# Create the upload folder
upload_folder = "uploads/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

# Set maximum size of the file
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

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
            db_filepath = os.path.join(
                app.config["UPLOAD_FOLDER"], secure_filename(f.filename)
            )
            f.save(db_filepath)  # this will secure the file

            # Execute core python script to decompose the TestStand database file
            csv_file_count = ts_db.main(db_filepath)

            # Purge uploads folder after script is finished
            for file in os.listdir(upload_folder):
                if file.endswith(".mdb"):
                    os.remove(os.path.join(upload_folder, file))

            return f"MDB processed:: {csv_file_count} CSV files exported to C:\\TestStand Results"

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
