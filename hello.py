# http://127.0.0.1:5000
from flask import Flask, render_template


# Create a Flask instance
app = Flask(__name__)


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


# Create custom error pages

# invalid url 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

