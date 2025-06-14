from flask import Flask, render_template, redirect, url_for, jsonify
from utils.db import get_config_value, update_config_value, get_status
from forms import AISDispatcherForm, DispatchActiveForm

from config import Config


app = Flask(__name__)
app.config.from_object(Config)


@app.route("/", methods=["GET", "POST"])
@app.route("/ais", methods=["GET", "POST"])
def index():
    active = get_config_value("active")
    if active:
        return redirect("/sending")
    config_form = AISDispatcherForm()
    if config_form.validate_on_submit():
        update_config_value("active", 1)
        update_config_value("interval", config_form.dispatch_interval.data)
        update_config_value("data_max", int(config_form.data_max.data)*1024)
        update_config_value("data_sent", 0)
        return redirect(url_for("sending"))

    listener_status = get_status("listener")
    return render_template("ais.html", form=config_form, listener_status=listener_status)


@app.route("/sending", methods=["GET", "POST"])
def sending():
    active = get_config_value("active")
    if not active:
        return redirect(url_for("index"))
    dispatch_active_form = DispatchActiveForm()
    if dispatch_active_form.validate_on_submit():
        update_config_value("active", "")
        return redirect(url_for("index"))
    listener_status = get_status("listener")
    dispatcher_status = get_status("dispatcher")
    return render_template(
        "dispatching.html",
        title="Dispatching",
        form=dispatch_active_form,
        listener_status=listener_status,
        dispatcher_status=dispatcher_status,
    )


@app.route("/data_size", methods=["GET"])
def data_size():
    return jsonify({"total_sent": get_config_value("data_sent")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
