# http://127.0.0.1:5000
# base app
from flask import Flask, render_template, flash, request, redirect, url_for

#forms & login
from webforms import LoginForm, UserForm, PostForm, PasswordForm, NamerForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager,login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# rich text editor
from flask_ckeditor import CKEditor

# database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# others
from datetime import datetime, date


# Create a Flask instance
# def create_app():
app = Flask(__name__)
ckeditor = CKEditor(app)
app.debug = True

        
# Add Database
# old db - sqlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# new db - mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://upoziyykdejpza:c4e470e9c28407e3a039b46ab399177be7ba9eda949c6b8b0727030d2b73c13b@ec2-18-215-41-121.compute-1.amazonaws.com:5432/ddi56vtf2uo5lv'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:kiirosan@localhost:3306/our_users'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know!!"
db = SQLAlchemy()
migrate = Migrate(app, db)

db.init_app(app)
app.app_context().push()

# Configure Profile Picture save path
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # return app
# app = create_app()

# Flask Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "User needs to be logged in to access this page"
login_manager.login_message_category = "warning"



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create a Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        # if user exists, check hash and compare with the one entered
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password - Try Again!!', 'warning')
        else:
            flash("User Doesn't Exist! Sign up instead!", 'warning')
    return render_template('login.html', form=form)

# Create Log out Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logout Successful!', 'success')
    return redirect(url_for('login'))

# Create a Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    return render_template('dashboard.html')


# open individual blogs in a new page
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# edit individual blogposts
@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        # update database
        db.session.add(post)
        db.session.commit()

        # flash success message
        flash('Post Successfully Updated!', 'success')
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.poster.id:
        # data already on the form, only needs to be edited
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash('You are not authorized to edit this post!', 'danger')
        # grab all posts from database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

# delete individual posts
@app.route('/posts/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post Deleted Successfully!', 'success')
            # grab all posts from database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            # return error message
            flash('Whoops! There was a problem deleting the post. Please try again later!')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash("You aren't authorized to delete this post!", 'danger')
            # grab all posts from database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


# Add post page
@app.route('/add-post', methods=['GET','POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id

        # passing the data entered in the form to the post variable
        post = Posts(title=form.title.data, content=form.content.data, 
                        poster_id=poster, slug=form.slug.data)

        # clearing the form
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''

        # add post data into database
        db.session.add(post)
        db.session.commit()

        # return a message when the form is submitted
        flash("Blog Post Submiitted Successfully!")
        return redirect(url_for('post', id=post.id))

    # redirect all this info to the webpage
    return render_template('add_post.html', form=form)

@app.route('/posts')
def posts():
    # grab all posts from database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

# json thing
@app.route('/date')
def get_current_date():
    test = {
            'Date': '22-10-2022', 
            'Pizza': 'Pepperoni', 
            'OrderNo': '110293'
            }
    return test


# Update Database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.fav_color= request.form['fav_color']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        # grab profile picture file name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # set UUID
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
         # save the image
        name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        # save the string in db
        name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            flash('User Updated Successfully!', 'success')
            return render_template('dashboard.html', form=form, 
                        name_to_update=name_to_update)
        except:
            flash('Error! Looks like there was a problem. Try Again!', 'warning')
            return render_template('update.html', form=form, 
                        name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, 
                        name_to_update=name_to_update, id=id)
        
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!')

        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', 
            form=form, name=name, 
            our_users=our_users)

    except:
        flash('Whoo[s! There was a problem deleting the user.')
        return render_template('add_user.html', 
            form=form, name=name, 
            our_users=our_users)

# Create a route decorator
@app.route('/')
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



# Testing password hashing
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        # clear the form
        form.email.data = ''
        form.password_hash.data = ''

        # look up user by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        # check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

        flash("Form Submitted Successfully!")

    return render_template('test_pw.html', 
            email=email, password=password, 
            pw_to_check=pw_to_check,
            passed = passed, form=form)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hashing the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")

            user = Users(name=form.name.data, username=form.username.data, email=form.email.data, password_hash=hashed_pw, fav_color=form.fav_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.fav_color.data = ''
        form.email.data = ''
        form.password_hash = ''
        flash("User Added Successfully!")
    
    our_users = Users.query.order_by(Users.date_added)

    return render_template('add_user.html', 
            form=form, name=name, 
            our_users=our_users)

# pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create an admin page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 19:
        return render_template('admin.html')
    else:
        flash('Sorry, you must have the Admin privilege to access this page.', 'danger')
        return redirect(url_for('dashboard'))
# Create Search Function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    # get data from submitted form
    post.searched = form.searched.data
    # query the database for results
    posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
    posts = posts.order_by(Posts.title).all()

    if form.validate_on_submit():
        post.searched = form.searched.data
        return render_template('search.html', 
            form=form, searched=post.searched, posts=posts)


# DB Models

# create a blog plot Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign key to link users (refer primary key in Users db)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # password
    password_hash = db.Column(db.String(128))
    # user can have many posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create a string 
    def __repr__(self):
        return '<Name %r>' %self.name


# Create custom error pages

# invalid url 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

