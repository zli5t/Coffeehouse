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

@app.route("/")
def index_page():
    return render_template("index.html")

def get_user(email, password):
    if not (email and password):
        return None
    user = User.query.filter_by(email=email).first()
    if (user and user.has_password(password)):
        return user 
    else:
        return None

def login(user):
    session["user"] = user

def logout(user):
    pass
   

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user = get_user(request.form["email"], request.form["password"])
        if (user):
            login(user)
            return redirect(url_for('home_page'))
        else:
            flash('Invalid login')
            return redirect(url_for('login_page'))
    else:
        return redirect(url_for('index_page'))

@app.route('/home')
def home_page():
    user = session["user"]
    return render_template("home.html", name=user.name)
    
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
