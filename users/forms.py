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


def validate_password(form, field):
    p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^a-zA-Z\d\s])')

    if not p.match(field.data):
        raise ValidationError("Password must contain at least one digit, one lowercase word character,"
                              " one uppercase word character, and one special character.")


def validate_dob(form, field):
    pass


def validate_postcode(form, field):
    pass

class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email(message="Invalid Email Address")])
    firstname = StringField(validators=[DataRequired(), name_character_check])
    lastname = StringField(validators=[DataRequired(), name_character_check])
    phone = StringField(validators=[DataRequired(), validate_phone])
    dob = StringField(validators=[DataRequired(), validate_dob])
    postcode = StringField(validators=[DataRequired(), validate_postcode])
    password = PasswordField(validators=[DataRequired(), Length(min=6, max=12), validate_password])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password',
                                                                         message="Passwords do not match.")])
    submit = SubmitField()
