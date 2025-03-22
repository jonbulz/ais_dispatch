from flask import Flask, render_template, request, redirect, url_for
from utils.db import get_config_value, update_config_value

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    interval = get_config_value("interval")
    active = get_config_value("active")
    config = {"interval": interval, "active": active}

    if request.method == "POST":
        new_interval = request.form["interval"]
        new_active = request.form["active"]

        update_config_value("interval", new_interval)
        update_config_value("active", new_active)

        return redirect(url_for("index"))

    return render_template("index.html", config=config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
