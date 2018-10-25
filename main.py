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
    allowed_routes =['login', 'signup', 'blog_list', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['enter-username']
        password = request.form['enter-pw']        
        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "Username does not exist"
            return render_template('login.html', username=username, username_error=username_error)
        if user.password != password:
            enter_pw_error = "Invalid password"
            return render_template('login.html', username=username, enter_pw_error=enter_pw_error)
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
        create_username_error = ''
        create_pw_error = ''
        confirm_pw_error = ''
        existiing_user = User.query.filter_by(username=username).first()
        if existiing_user:
            create_username_error = "Username already exists"
        if username.strip() == '' or len(username) < 3 or ' ' in username:
            create_username_error = "Invalid username (Must be at least 3 characters and contain no spaces)"
        if password.strip == '' or len(password) < 3 or ' ' in password:
            create_pw_error = "Invalid password (Must be at least 3 characters and contain no spaces)"
        if verify != password:
            confirm_pw_error = "Passwords do not match"
        if create_username_error or create_pw_error or confirm_pw_error:
            return render_template('signup.html', create_username_error=create_username_error, username=username,
                                    create_pw_error=create_pw_error, confirm_pw_error=confirm_pw_error)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/addpost')

            
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
        owner = User.query.filter_by(username=session['username']).first()
        if title.strip() == '':
            title_error = "Please enter a blog title"
        if body.strip() == '':
            body_error = "Please write a blog entry"
        if title_error == '' and body_error == '':
            new_blog = Blog(title, body, owner)      
            db.session.add(new_blog)
            db.session.commit()
            id = new_blog.id
            blogs = Blog.query.filter_by(id=id).all()
            users = User.query.all()
            return render_template('single_entry.html', blogs=blogs, users=users)
            
    return render_template('addpost.html', title_error=title_error, body_error=body_error, title=title, body=body)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/blog', methods=['POST','GET'])
def blog_list():
    id = request.args.get('id')
    user_id = request.args.get('user_id')
    blogs = Blog.query.all()
    users = User.query.all()
    if id:
        blogs = Blog.query.filter_by(id=id).all()
        return render_template('single_entry.html', blogs=blogs, users=users)
    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', blogs=blogs, users=users)


    return render_template('blog.html', blogs=blogs, users=users)

@app.route("/", methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
if __name__ == '__main__':
    app.run()