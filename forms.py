from flask_wtf import Form
from models import User
from wtforms import StringField,PasswordField,TextAreaField
from wtforms.validators import (DataRequired,Regexp,ValidationError,Email,Length,EqualTo)


def name_exists(form,field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("FUCK YOU")
def email_exists(form,field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("FUCK YOU")

class RegisterForm(Form):
    username = StringField(
        "Username",
        validators=[
            DataRequired(), #somowthing must be there
            Regexp(
                r'^[A-Za-z0-9_]*$',
                message = "username is 1 word letters nums undies only"
            ), name_exists
        ])
    email = StringField(
        "email",
        validators=[
            DataRequired(),  # somowthing must be there
            Email(), #email regex pattern requtired
             email_exists
        ])
    password = PasswordField(
        "password",
        validators=[
            DataRequired(),  # somowthing must be there
            Length(min=2),
            EqualTo("password2",message="passwords must match") #must be equal to password 2 password field
            #if not show the message
        ])
    password2 = PasswordField(
        "confirm password2",
        validators=[
            DataRequired(),  # somowthing must be there

        ])

class LoginForm(Form):
    email = StringField("email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired()])

class PostForm(Form):
    content = TextAreaField("SUH BRUH",validators=[DataRequired()])