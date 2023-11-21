from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class DrawForm(FlaskForm):

    def validate(self, **kwargs):
        standard_validators = super().validate()
        if standard_validators:
            values = list(kwargs.values())
            if any(values.count(element) > 1 for element in values):
                raise ValidationError("Each number must be unique")
            else:
                return True

        return False

    number1 = IntegerField(id='no1', validators=[InputRequired(), NumberRange(min=1, max=60)])
    number2 = IntegerField(id='no2', validators=[InputRequired(), NumberRange(min=1, max=60)])
    number3 = IntegerField(id='no3', validators=[InputRequired(), NumberRange(min=1, max=60)])
    number4 = IntegerField(id='no4', validators=[InputRequired(), NumberRange(min=1, max=60)])
    number5 = IntegerField(id='no5', validators=[InputRequired(), NumberRange(min=1, max=60)])
    number6 = IntegerField(id='no6', validators=[InputRequired(), NumberRange(min=1, max=60)])
    submit = SubmitField("Submit Draw")
