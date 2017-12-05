# http://education.launchcode.org/web-fundamentals/assignments/build-a-blog/

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

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
        # TODO consider how to use separate 'user-sigup' module here

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()

            session['email'] = email
            return redirect('/')
        else:
            flash("email already registered")
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
            return redirect('/')
        else:
            flash("password is incorrect or user doesn't exist", "error")
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()
    print('owner:', owner)

    if request.method == 'POST':
        print('Inside index() if:')
        # user is trying to submit a blog post
        title = request.form['title']
        body = request.form['body']
        print('before new post')
        new_post = Post(title, body, owner)
        db.session.add(new_post)
        #db.session.add(Post(request.form['title'], request.form['body'], owner)) #alt one-liner
        db.session.commit()

    posts = Post.query.filter_by(owner=owner).all()
    
    return render_template('index.html', title="Build a Blog", 
        posts=posts)

if __name__ == '__main__':
    app.run()