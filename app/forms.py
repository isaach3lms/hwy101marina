import re

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from .content import CONTACT


def _phone(form, field):
    digits = re.sub(r"\D", "", field.data or "")
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) != 10:
        raise ValidationError("Enter a 10 digit phone number.")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Phone number", validators=[DataRequired(), Length(max=30), _phone])
    interest = SelectField("I am interested in", choices=CONTACT["interests"], validators=[DataRequired()])
    message = TextAreaField("Question", validators=[DataRequired(), Length(max=2000)])
    # Honeypot: real visitors never see or fill this field.
    website = StringField("Website")
