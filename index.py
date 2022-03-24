from unicodedata import name
from flask import Flask, redirect, url_for, render_template
from flask_migrate import Migrate
from models import db, InfoModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://yhmydmkq:ShEKjzmafUtoC3Ntek8Sf_mVfxO-gGtg@raja.db.elephantsql.com:5432/yhmydmkq"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def home():
    return redirect(url_for("page", name="login"))

@app.route("/<name>/")
def page(name):
    return render_template(name + ".html")

if __name__ == "__main__":
    app.run()