import re

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from .content import CONTACT


def _phone(form, field):
    digits = re.sub(r"\D", "", field.data or "")
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) != 10:
        raise ValidationError("Enter a 10 digit phone number.")


_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _email(form, field):
    if field.data and not _EMAIL.match(field.data.strip()):
        raise ValidationError("Enter a valid email address.")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email (optional)", validators=[Optional(), Length(max=120), _email])
    phone = StringField("Phone number", validators=[DataRequired(), Length(max=30), _phone])
    interest = SelectField("I am interested in", choices=CONTACT["interests"], validators=[DataRequired()])
    message = TextAreaField("Question", validators=[DataRequired(), Length(max=2000)])
    # Honeypot: real visitors never see or fill this field.
    website = StringField("Website")
