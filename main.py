from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:yes@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes =['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['enter-username']
        password = request.form['enter-pw']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/addpost')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['create-username']
        password = request.form['create-pw']
        verify = request.form['confirm-pw']

        existiing_user = User.query.filter_by(username=username).first()
        if not existiing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/addpost')
        else:
            return '<h1>Duplicate User</h1>'
            
    return render_template('signup.html')

@app.route('/addpost', methods=['POST','GET'])
def addpost():
    title = ''
    body = ''
    title_error = ''
    body_error =''
    if request.method == 'POST':
        title = request.form['new-title']
        body = request.form['new-body']
        if title.strip() == '':
            title_error = "Please enter a blog title"
        if body.strip() == '':
            body_error = "Please write a blog entry"
        if title_error == '' and body_error == '':
            new_blog = Blog(title, body)      
            db.session.add(new_blog)
            db.session.commit()
            id = new_blog.id
            blogs = Blog.query.filter_by(id=id).all()
            return render_template('single_entry.html', blogs=blogs)
            
    return render_template('addpost.html', title_error=title_error, body_error=body_error, title=title, body=body)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route("/", methods=['POST','GET'])
def index():
    id = request.args.get('id')
    if id:
        blogs = Blog.query.filter_by(id=id).all()
        return render_template('single_entry.html', blogs=blogs)

    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)



if __name__ == '__main__':
    app.run()