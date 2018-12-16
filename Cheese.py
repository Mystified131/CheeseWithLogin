from flask import Flask, request, render_template, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import datetime, os, cgi, hashlib, random

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Cheese:Jackson1313@localhost:8889/Cheese'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)

class Cheese(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(120))
    name = db.Column(db.String(120))
    description = db.Column(db.String(120))

    def __init__(self, timestamp, name, description):
        self.timestamp = timestamp
        self.name = name
        self.description = description

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password

def make_salt():
    sal = ""
    for elem in range(5):
        num1 = random.randrange(9)
        num2 = str(num1)
        sal += num2
    return sal
    
def make_pw_hash(password, keynum):
    hashlist = []
    hashlist.append(hashlib.md5(str.encode(password)).hexdigest())
    hashlist.append(hashlib.sha1(str.encode(password)).hexdigest())
    hashlist.append(hashlib.sha224(str.encode(password)).hexdigest())
    hashlist.append(hashlib.sha256(str.encode(password)).hexdigest())
    hashlist.append(hashlib.sha384(str.encode(password)).hexdigest())
    hashlist.append(hashlib.sha512(str.encode(password)).hexdigest())
    hash = hashlist[keynum]
    return hash

def check_pw_hash(password, hash):
    hash2 = hash[6:]
    hash3 = int(hash[5])
    if make_pw_hash(password, hash3) == hash2:
        return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.password):
            session['email'] = email
            #flash("Logged in")
            return redirect('/cheese')
        elif not user:
            flash("User does not exist")
            return redirect('/signup')
        else:
            flash('User password incorrect')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not email or not password or not verify:
            flash("Please fill in all form spaces")
            return redirect('/signup')
        if password != verify:
            flash("Password and Password Verify fields do not match")
            return redirect('/signup')
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            salt = make_salt()
            keynm = random.randrange(6)
            hash = make_pw_hash(password, keynm)
            keyst = str(keynm)
            password = salt + keyst + hash
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash("Signed In")
            return redirect('/cheese')
        else:
            flash('Duplicate User')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

@app.route("/cheese", methods =['GET', 'POST'])
def index():
    right_now = datetime.datetime.now().isoformat()
    list = []

    for i in right_now:
        if i.isnumeric():
           list.append(i)

    tim = "".join(list)
    session['timestamp'] = tim
    cheeses = Cheese.query.all()
    cheeselist = []
    for cheese in cheeses:
        cheesestr = cheese.name + ": " + cheese.description
        cheeselist.append(cheesestr)
    cheeselist.sort()
    return render_template('index.html', cheeses = cheeselist)

@app.route("/add", methods =['GET', 'POST'])
def add():
    error = ""
    cheesename = request.form["name"]
    cheesedescript = request.form["descript"]
    timestamp = session['timestamp']
    name = cgi.escape(cheesename)
    name = name.lower()
    description = cgi.escape(cheesedescript)
    old_cheese = Cheese.query.filter_by(name=name).first()
    if old_cheese or not name or not description:
        if not description:
            error = "Please describe the cheese, in order to add it."
        if not name:
            error = "There is no cheese with no name."
        if old_cheese:
            error = "That cheese is already in the database."
        cheeses = Cheese.query.all()
        cheeselist = []
        for cheese in cheeses:
            cheesestr = cheese.name + ": " + cheese.description
            cheeselist.append(cheesestr)
        cheeselist.sort()
        return render_template('index.html', cheeses = cheeselist, error = error)
    new_cheese = Cheese(timestamp, name, description)
    db.session.add(new_cheese)
    db.session.commit()
    cheeses = Cheese.query.all()
    cheeselist = []
    for cheese in cheeses:
        cheesestr = cheese.name + ": " + cheese.description
        cheeselist.append(cheesestr)
    cheeselist.sort()
    return render_template('index.html', cheeses = cheeselist)

@app.route("/remove", methods =['GET', 'POST'])
def remove():
    cheesename = request.form["remname"]
    name = cgi.escape(cheesename)
    the_cheese = Cheese.query.filter_by(name=name).first()
    if the_cheese:
        db.session.delete(the_cheese)
        db.session.commit()
        cheeses = Cheese.query.all()
        cheeselist = []
        for cheese in cheeses:
            cheesestr = cheese.name + ": " + cheese.description
            cheeselist.append(cheesestr)
        cheeselist.sort()
        return render_template('index.html', cheeses = cheeselist)
    else:
        error2 = "That cheese is not in the database."
        cheeses = Cheese.query.all()
        cheeselist = []
        for cheese in cheeses:
            cheesestr = cheese.name + ": " + cheese.description
            cheeselist.append(cheesestr)
        cheeselist.sort()
        return render_template('index.html', cheeses = cheeselist, error2 = error2)

## THE GHOST OF THE SHADOW ##

if __name__ == '__main__':
    app.run()



