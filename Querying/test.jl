# Creates code to interact with Julia

using PyCall

# Loads Python module
py"""
from flask import Flask, render_template, request
import os

app = Flask(_name_)

@app.route("/")
def hello_world():
    return "<p>Hello World</p>"

if _name_ == "_main_":
    app.run(debug=True,  host="0.0.0.0", port=8080)

"""