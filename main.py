# http://education.launchcode.org/web-fundamentals/assignments/build-a-blog/

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
# connection string 'mysqldatabase+using pymysql driver://username:password@the server the db lives on:port(default 8889 for mysql)/name of db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:youShallPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
# to disable a warning when the app is run on the command line
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# secret key is required to use sessions
app.secret_key = 'r937aGcys&b3PG'

db = SQLAlchemy(app)

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    # TODO, feild is 'ower_id', but constructor is 'owner'. But everything works (held over from 'get-it-done' project)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.title = name
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship(Post, backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

# check ALL incoming requests
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        # user is trying to register
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO validate user data

        valid_email = re.compile('[^@]+@[^@]+\.[^@]+')
        if not valid_email.search(email):
            flash('Please enter a valid email address')
            return render_template('register.html', email=email)
        if not password or password.isspace() or not(5 < len(password) < 21):
            flash('Please submit a valid password (3-20 characters)')
            return render_template('register.html', email=email)
        if not (password == verify):
            flash('passwords need to match')
            return render_template('register.html', email=email)



        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()

            session['email'] = email
            return redirect('/blog')
        else:
            flash("email already registered", "error")
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        # user is trying to login
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email # set the session dict at the key 'email' to the value of email
            flash('Logged in')
            return redirect('/blog')
        else:
            flash("password is incorrect or user doesn't exist", "error")
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/blog')
def blog():

    if request.args:  # if the request had any query parameters
        # display a single post
        id = request.args.get('id')
        post = Post.query.filter_by(id=id).first()
        # post = Post.query.filter_by(id=request.args.get('id') # one-liner
        return render_template('post.html', post=post)

    owner = User.query.filter_by(email=session['email']).first()
    posts = Post.query.filter_by(owner=owner).all()

    return render_template('posts.html', title="Blogbook", owner=owner, posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        # user is trying to submit a blog post

        title = request.form['title']
        body = request.form['body']

        #validate data
        if not title or title.isspace() or not body or body.isspace():
            flash('Please add a Title and Body', 'error')
            return render_template('newpost.html', title=title, body=body)

        new_post = Post(title, body, owner)
        db.session.add(new_post)
        #db.session.add(Post(request.form['title'], request.form['body'], owner)) #alt one-liner
        db.session.commit()

        # I'm surprised that this line works because the new_post variable assignment doesn't know about the id field, right?
        # my best guess is that new_post gets updated when we write db.session.commit()
        new_post_id = new_post.id
        return redirect('/blog?id=' + str(new_post_id))
    
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()