from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, InputRequired, EqualTo, ValidationError
from datetime import datetime
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
    p = re.compile('(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}')

    validity = False

    if p.match(field.data):
        d, m, y = int(field.data[0:2]), int(field.data[3:5]), int(field.data[6:])
        print(d, m, y)
        if 1900 <= y <= datetime.now().year:
            if m in ["09", "04", "06", "11"] and d <= 30:
                validity = True
            elif m == "02":
                # divisible by 100 but not 400 = not leap year (1900 not leap year)
                if y % 4 == 0 or (y % 400 == 0 and y % 100 != 0):
                    if d <= 29:
                        validity = True
            elif m not in ["02", "09", "04", "06", "11"]:
                validity = True

    if not validity:
        raise ValidationError("Date is not of the form DD/MM/YYYY, or it is not a valid date.")

def validate_postcode(form, field):
    pass

class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(message="Invalid Email Address")])
    firstname = StringField(validators=[InputRequired(), name_character_check])
    lastname = StringField(validators=[InputRequired(), name_character_check])
    phone = StringField(validators=[InputRequired(), validate_phone])
    dob = StringField(validators=[InputRequired(), validate_dob])
    postcode = StringField(validators=[InputRequired(), validate_postcode])
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=12), validate_password])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password',
                                                                         message="Passwords do not match.")])
    submit = SubmitField()
