from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, DataRequired, EqualTo, ValidationError
import re


def name_character_check(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"

    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")

def validate_phone(form, field):

    p = re.compile('[0-9]{4}\-[0-9]{3}\-[0-9]{4}')

    if not p.match(field.data):
        raise ValidationError("Phone number is not of the form XXXX-XXX-XXXX.")

class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email(message="Invalid Email Address")])
    firstname = StringField(validators=[DataRequired(), name_character_check])
    lastname = StringField(validators=[DataRequired(), name_character_check])
    phone = StringField(validators=[DataRequired(), validate_phone])
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()

