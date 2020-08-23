from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField

from wtforms.validators import Required, NumberRange, ValidationError

class EditScr(FlaskForm):
  
    scrDay = IntegerField('Day', validators=[NumberRange(min=1, max=31),Required(message=u'Day is required')])
    scrMonth = IntegerField('Month', validators=[NumberRange(min=1, max=12),Required(message=u'Month is required')])
    scrYear = IntegerField('Year', validators=[NumberRange(min=2020, max=2120),Required(message=u'Year is required')])
    scrHours = IntegerField('Hours',validators=[NumberRange(min=1, max=23),Required(message=u'Hours are required')])
    scrMinutes = IntegerField('Minutes',validators=[NumberRange(min=0, max=59),Required(message=u'Minutes are required')])

    submit = SubmitField('Add Screening')



