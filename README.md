# Flasker

## <a name="toc">Table of Contents</a>
1. [Introduction](#intro)
2. [Installation Instructions](#install)
  <br>2.1. Download the code
  <br>2.2. Update `create_db.py`
  <br>2.3. Create a `.env` file
  <br>2.4. Import model from the terminal
  <br>2.5. Hiding the necessary files using `.gitignore`
3. [Running the Webapp in Local Machine](#run)
4. [Future Plans](#plans)

---

## 1. <a name="intro">Introduction</a> 
###### [Back to Table of Contents](#toc)
This is a blogging website created in Flask Python using a [Codemy playlist](https://youtube.com/playlist?list=PLCC34OHNcOtolz2Vd9ZSeSXWc8Bq23yEz). I have made many changes and modified the design of the website as to my liking. Additional features will also be addressed.

#### Here are some screenshots of the website in the Development Environment:
![profile](static\images\ss_profile.png)
![login](static\images\ss_login.png)
![home](static\images\ss_home.png)
![addpost](static\images\ss_addpost.png)
![search](static\images\ss_search.png)

---

## 2. <a name="install">Installation Instructions</a>
###### [Back to Table of Contents](#toc)

> Note: I have used Git Bash for the project and provided the code for the same.

### 2.1. Download the code

> Note: `hello.py` from the playlist has been changed to `app.py`.
- Fork and clone this repository to your local machine.
- Create a virtual environment ([link](https://www.youtube.com/watch?v=0Qxtt4veJIc&list=PLCC34OHNcOtolz2Vd9ZSeSXWc8Bq23yEz&index=1))
- Activate the virtual environment.
- Install all the necessary dependencies and modules inside the virtual environment:
```
pip install -r requirements
```

### 2.2. Update `create_db.py`
This is for MySQL only. Before taking data from the users, it is necessary to make sure the database exists, where all the required information for the website is stored in your local device.

> Note: The database is created with the name `our_users`. You will see the db name in the SQLALCHEMY_DATABASE_URI as well.

#### Steps to follow:
- Uncomment the entire `create_db.py` file.
- Execute or run the .py file **just once**, to create the database in your local device.
- Comment it again as the database with the name `our_users` exists now.

### 2.3. Create a `.env` file 
Paste the following code and modify the code according to the comments.

```
# secret key 
# replace the string with your secret key.
SECRET_KEY = "my super secret key that no one is supposed to know!!"


# database 
# uncomment whichever database you are using.
# Replace {username} and {password} with your MySQL username and password.

# sqllite
# SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'

# mysql
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@localhost:3306/our_users'
```
### 2.4. Import model from the terminal ([link](https://www.youtube.com/watch?v=Q2QmST-cSwc&list=PLCC34OHNcOtolz2Vd9ZSeSXWc8Bq23yEz&index=8) to the playlist video)
Open the python interative shell

- If using linux terminal:
```bash
$ winpty python
```
- Create db
```python
>>> from app import db
>>> db.create_all()
```

2.5. Hiding the necessary files using `.gitignore`
Make sure to create a `.gitignore` file to hide neccessary files like `.env` and `.gitignore`.
For this, just create a file with the name `.gitignore` in your project folder and copy paste the below code:
```
.gitignore
virt/
.env
```

---

## 3. <a name="run">Run the Webapp in Local Machine</a>
###### [Back to Table of Contents](#toc)

- Open your project folder in Git Bash.
- Activate your virtual environment.
```
$ source {virt_env_name}/bin/activate
```
- Open `app.py` file and make the following modifications to switch to the development environment.
```python
# configuring flask app
app.config.from_object('config.Config')
# -- development env
app.config.from_object('config.DevConfig')
# -- production env
# app.config.from_object('config.ProdConfig')
```
> Note: To switch back to Production Environment, just comment the development env code and uncomment the production env code.

- Set Flask app and run.
```
$ export FLASK_APP=app.py
$ export FLASK_DEBUG=1
$ flask run
```
Here, setting FLASK_DEBUG=1 is only for the development environment.

---

## 4. <a name="plans">Future Plans</a>
###### [Back to Table of Contents](#toc)
- Create a comment section under individual posts.
- Add likes and comments in each post and display it in Author's list of work in their profile.
- Add a CKE Editor for About Author section.
