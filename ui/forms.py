from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired


class AISDispatcherForm(FlaskForm):
    data_max = IntegerField("Maximum Data")
    dispatch_interval = IntegerField("Interval in s", validators=[DataRequired()])
    start_dispatch = SubmitField("Start")


class DispatchActiveForm(FlaskForm):
    stop_dispatch = SubmitField("Stop")
