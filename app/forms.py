from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectMultipleField, widgets, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from app import cocktailRecommender

from app.models import User



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'Username'})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2')], render_kw={'placeholder': 'Password'})
    password2 = PasswordField('Repeat password', validators=[DataRequired()], render_kw={'placeholder': 'Password Confirmation'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Choose a different username')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please choose a different email')



class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(('Submit'))


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EvalForm(FlaskForm):
    opinions = ['Bad','Neutral', 'Good']
    op_list = [(x, x) for x in opinions]
    options = MultiCheckboxField('Label', choices=op_list)
    submit = SubmitField('Submit')


class SimpleForm(FlaskForm):
    fruits, alco, nonalco, others = cocktailRecommender.get_general_taxonomy()
    fruits = sorted(fruits)
    alco = sorted(alco)
    nonalco = sorted(nonalco)
    others = sorted(others)

    fruit_list = [(x.title(), x.title()) for x in fruits if x !='']
    alco_list = [(x.title(), x.title()) for x in alco if x !='']
    nonalco_list = [(x.title(), x.title()) for x in nonalco if x !='']
    others_list = [(x.title(), x.title()) for x in others if x !='']

    fruits_cb = MultiCheckboxField('Label', choices=fruit_list)
    alco_cb = MultiCheckboxField('Label', choices=alco_list)
    nonalco_cb = MultiCheckboxField('Label', choices=nonalco_list)
    others_cb = MultiCheckboxField('Label', choices=others_list)

    style = {'type': 'button', 'class' : 'btn-primary'}
    submit = SubmitField('search')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')