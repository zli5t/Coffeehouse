import os, hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, \
                    session
            
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = \
   '\xfaz\xb8|\x10\xd2#\xe0\x96\xb7\x13\xe2:9\xcdE\xeb\xf5\xa7x\xb9\x97\xa2\xb7'
db = SQLAlchemy(app)

def gen_hash(password):
    hash_alg = hashlib.sha512()
    hash_alg.update(password)
    return hash_alg.hexdigest()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String, unique=False)
    
    def __init__(self, email, password):
        self.email = email
        self.password_hash = gen_hash(password)

    def __repr__(self):
        return '<User %r>' % self.email

    def has_password(self, password):
        return self.password_hash == gen_hash(password)

def login(user):
    session["user_id"] = user.id


def retrieve_user(email, password):
    if not (email and password):
        return None
    user = User.query.filter_by(email=email).first()
    if (user and user.has_password(password)):
        return user 
    else:
        return None

def get_user(id):
    user = User.query.filter_by(id=id).first()
    if (user):
        print user.id, user.name, user.email
    return user

def logged_in():
    return ('user_id' in session) and session['user_id']

@app.route("/") 
def index():
    if logged_in():
        return render_template("home.html", 
                                user=get_user(session["user_id"]))
    else:
        return render_template("login.html")

@app.route("/login", methods=['POST'])
def login():
    if not logged_in():
        user = retrieve_user(request.form["email"], request.form["password"])
        if (user):
            session['user_id'] = user.id
        else:
            flash('Invalid login')
    return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session["user_id"] = 0
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
