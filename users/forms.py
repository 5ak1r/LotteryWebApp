from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Email, Length, InputRequired, EqualTo, ValidationError
from datetime import datetime
import re

# custom validators for registration using regex
def name_character_check(form, field):
    # name cannot include the special characters listed below
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"

    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")


def validate_phone(form, field):
    # phone number must be of the form 'XXXX-XXX-XXXX' where X is a digit (0-9)
    p = re.compile(r'^[0-9]{4}\-[0-9]{3}\-[0-9]{4}$')

    if not p.match(field.data):
        raise ValidationError("Phone number is not of the form XXXX-XXX-XXXX.")


def validate_password(form, field):
    # password must include at least one digit, lower case word character, upper case word character and special character
    p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^a-zA-Z\d\s])')

    if not p.match(field.data):
        raise ValidationError("Password must contain at least one digit, one lowercase word character,"
                              " one uppercase word character, and one special character.")


def validate_dob(form, field):
    p = re.compile(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')

    validity = False

    # if string format is correct, form DD/MM/YYYY
    if p.match(field.data):
        # checking date is valid, accounting for leap years (not required)
        d, m, y = int(field.data[0:2]), field.data[3:5], int(field.data[6:])
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
    # postcode must be of the forms XY YXX, XYY YXX or XXY YXX, where X is a capital letter; Y is an integer (0-9)
    p = re.compile(r'^([A-Z])([0-9]|[0-9]{2}|[A-Z][0-9])( [0-9][A-Z]{2})$')

    if not p.match(field.data):
        raise ValidationError("Postcode is not of any of the required forms: XY YXX, XYY YXX, XXY YXX.")
    
    
# registration flask form
class RegisterForm(FlaskForm):
    # inputs required for all fields
    email = StringField(validators=[InputRequired(), Email(message="Invalid Email Address")])
    firstname = StringField(validators=[InputRequired(), name_character_check])
    lastname = StringField(validators=[InputRequired(), name_character_check])
    phone = StringField(validators=[InputRequired(), validate_phone])
    dob = StringField(validators=[InputRequired(), validate_dob])
    postcode = StringField(validators=[InputRequired(), validate_postcode])
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=12), validate_password])
    # must match password
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password',
                                                                         message="Passwords do not match.")])
    submit = SubmitField()


# login flask form
class LoginForm(FlaskForm):
    # no field can be empty
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    postcode = StringField(validators=[InputRequired()])
    pin = StringField(validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()


# password change flask form
class PasswordForm(FlaskForm):
    current_password = PasswordField(id='password', validators=[InputRequired()])
    show_password = BooleanField('Show password', id='check')
    new_password = PasswordField(validators=[InputRequired(), Length(min=6, max=12, message="Must be between 6 and 12 characters in length"), validate_password])
    confirm_new_password = PasswordField(validators=[InputRequired(), EqualTo('new_password', message='Both new password fields must be equal')])
    submit = SubmitField('Change Password')