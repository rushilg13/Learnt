from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import EmailField
from flask_pymongo import pymongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Cant_say'
class inputForm(Form):
    fname = StringField('fname', validators=[DataRequired()])
    lname = StringField('lname', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired(), Email()])
    pass1 = PasswordField('pass1', validators=[DataRequired()])
    sub = SubmitField('Sign Up')

class inputFormlogin(Form):
    email = EmailField('email', validators=[DataRequired(), Email()])
    pass1 = PasswordField('pass1', validators=[DataRequired()])
    sub = SubmitField('Login')

class inputFormAdd(Form):
    to_learn = SelectMultipleField('to_learn', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')], validators=[DataRequired()])
    can_teach = SelectMultipleField('can_teach', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')], validators=[DataRequired()])
    sub = SubmitField('Add')

db_password = input("Password for database is:")
CONNECTION_STRING = f"mongodb+srv://VIT_Admin:{db_password}@vitdiaries.tpuku.mongodb.net/CouponShare?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('Learnt!')
user_collection = pymongo.collection.Collection(db, 'Users')
add_collection = pymongo.collection.Collection(db, 'Add')

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = inputForm()
    if request.method=="POST":
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        pass1 = form.pass1.data
        print(fname, lname, email, pass1)
        if request.method == 'POST':
            if user_collection.count_documents({"Email": email}):
                flash('User already Exists. Try Login!')
                return redirect(url_for('login'))
            else:
                cipher = generate_password_hash(pass1, method='sha256')
                user_collection.insert_one({'First Name': fname, 'Last Name': lname, 'Email': email, 'Password': cipher})
                session['email'] = email
                return render_template('home.html', fname = fname, lname = lname, email=session['email'])
        else:
            return redirect(url_for('home'))
    return render_template("signup.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form_login = inputFormlogin()
    if request.method=="POST":
        email = form_login.email.data
        pass1 = form_login.pass1.data
        if  request.method == 'POST':
            user = user_collection.find_one({"Email":email})
            if check_password_hash(user['Password'], pass1):
                print("item exists")
                session['email'] = email
                return render_template('home.html', fname = user['First Name'], lname = user['Last Name'], email=session['email'])
            else:
                print("item is not existed")
                flash('Invalid Credentials')
                return redirect('/login')
        else:
            return redirect('/login')
    return render_template("login.html", form_login=form_login)

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'email' not in session:
        cursor = add_collection.find()
        return render_template('home.html', cursor=cursor)
    else:
        form_add = inputFormAdd()
        if request.method=="POST":
            can_teach = form_add.can_teach.data
            to_learn = form_add.to_learn.data
            user = user_collection.find_one({"Email":email})
            if request.method=="POST":
                add_collection.insert_one({'Teach': can_teach, 'Learn': to_learn, 'Email':email, 'First_Name': user['First Name'], 'Last_Name': user['Last Name']})
                return redirect(url_for('home'))
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile')
def profile():
    if 'email' in session:
        user = user_collection.find_one({"Email":session['email']})
        details = add_collection.find({"Email":session['email']})
        print(user['First Name'], user['Last Name'])
    return render_template('profile.html', fname = user['First Name'], lname = user['Last Name'], email = user['Email'], details=details)

if __name__ == "__main__":
    app.run(debug=True)
