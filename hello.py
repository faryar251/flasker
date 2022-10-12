# http://127.0.0.1:5000k
# base app
from flask import Flask, render_template, flash

#form - take value
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

#form - validate data
from wtforms.validators import DataRequired

# database
from flask_sqlalchemy import SQLAlchemy

# others
from datetime import datetime

db = SQLAlchemy()

# Create a Flask instance
def create_app():
    app = Flask(__name__)
    app.debug = True
            
    # Add Database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # secret key
    app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know!!"
    db.init_app(app)
    app.app_context().push()

    return app
app = create_app()

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string 
    def __repr__(self):
        return '<Name %r>' %self.name


# create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField('Submit')

# create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField('Submit')



# jinja2 filters: safe, upper, lower, capitalize, trim, splitags

# Create a route decorator
@app.route('/')
# def index():
#     return '<h1>Hello World!</h1>'
def index():
    first_name = 'John'
    stuff = 'This is a bold Text.'
    fav_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
    test = {1: 'a', 2:'b', 3:'c'}

    return render_template('index.html', 
        first_name=first_name, 
        stuff=stuff,
        fav_pizza=fav_pizza, test=test)


# localhost:5000/user/name
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)


# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")

    return render_template('name.html', 
            name=name, 
            form=form)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User Added Successfully!")
    
    our_users = Users.query.order_by(Users.date_added)

    return render_template('add_user.html', 
            form=form, name=name, 
            our_users=our_users)


# Create custom error pages

# invalid url 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
