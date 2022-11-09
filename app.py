# base app
from flask import Flask, render_template, flash, request, redirect, url_for

#forms & login
from webforms import LoginForm, UserForm, PostForm, PasswordForm, NamerForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager,login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import uuid as uuid
import logging
import sys
import os

# rich text editor
from flask_ckeditor import CKEditor

# database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# others
from datetime import datetime, date


# Create a Flask instance
app = Flask(__name__)
ckeditor = CKEditor(app)
app.debug = True

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# configuring flask app
app.config.from_object('config.Config')
# -- development env
# app.config.from_object('config.DevConfig')
# -- production env
app.config.from_object('config.ProdConfig')

db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)
app.app_context().push()


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
                return redirect(url_for('posts'))
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
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('dashboard.html', posts=posts)


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
    if id == post_to_delete.poster.id or id == 3:
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
        flash("Blog Post Submiitted Successfully!", 'success')
        return redirect(url_for('post', id=post.id))

    # redirect all this info to the webpage
    return render_template('add_post.html', form=form)

@app.route('/')
def posts():
    # grab all posts from database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


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

        # check for profile pic
        if request.files['profile_pic']:
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
            db.session.commit()
            flash('User Updated Successfully!', 'success')
            return render_template('dashboard.html', 
                            form=form, 
                            name_to_update=name_to_update)

    else:
        return render_template('update.html', form=form, 
                        name_to_update=name_to_update, id=id)
        
@app.route('/delete/<int:id>')
@login_required
def delete(id):

    if id == current_user.id:
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
            flash('Whoosh! There was a problem deleting the user.')
            return render_template('add_user.html', 
                form=form, name=name, 
                our_users=our_users)
    else:
        flash('You are not authorized to delete this user.', 'danger')
        return redirect(url_for('dashboard'))


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
        flash("User Added Successfully!", 'success')
        return redirect(url_for("login"))
    
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
    our_users = Users.query.order_by(Users.date_added)

    if id == 3:
        return render_template('admin.html', 
                            our_users=our_users)
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
    posts = posts.filter(Posts.content.ilike('%' + post.searched + '%'))
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


