from unicodedata import name
from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("page", name="login"))

@app.route("/<name>/")
def page(name):
    return render_template(name + ".html")

if __name__ == "__main__":
    app.run()