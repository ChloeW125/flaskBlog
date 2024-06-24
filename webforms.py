# Holds all webform functions, classes, etc.

# Imports for form functionality
from flask_wtf import FlaskForm
#Import fields to be able to build form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
#Import validators to validate the string input (this validator in particular will validate the string)
from wtforms.validators import DataRequired, EqualTo, Length
# Import widgets for the forms
from wtforms.widgets import TextArea

#Create a user form class
class UserForm(FlaskForm):
    #Define the fields that we want using vars
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_colour = StringField("Favourite Colour")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create name form class
class NamerForm(FlaskForm):
    #Define the fields that we want using vars
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create password form class
class PasswordForm(FlaskForm):
    #Define the fields that we want using vars
    email = StringField("What's Your Email?", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a posts form
class PostForm(FlaskForm):
    # Fields in the form
    title = StringField("Title", validators=[DataRequired()])
    # TextArea widget to make large text box for content
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")