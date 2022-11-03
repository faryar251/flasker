from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField



# Create login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# create a posts form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Submit')


# create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords Must Match!")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    fav_color = StringField("Favorite Color")
    profile_pic = FileField("Profile Picture")
    about_author = TextAreaField("About Author")
    submit = SubmitField('Submit')

# create a form class
class PasswordForm(FlaskForm):
    email = StringField("Enter E-Mail:", validators=[DataRequired()])
    password_hash = PasswordField("Enter Password:", validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a search form
class SearchForm(FlaskForm):
    searched = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Submit")


# create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField('Submit')

