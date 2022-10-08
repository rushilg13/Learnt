from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import EmailField
from flask_pymongo import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson import ObjectId
load_dotenv()
import os

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
    to_learn = SelectMultipleField('to_learn', choices=[('Frontend', 'Frontend'), ('Backend', 'Backend'), ('App Development', 'App Devlopment'), ('Blockchain', 'Blockchain'), ('Design', 'Design'), ('Machine Learning', 'Machine Learning'), ('Artificial Intelligence', 'Artificial Intelligence')], validators=[DataRequired()])
    can_teach = SelectMultipleField('can_teach', choices=[('Frontend', 'Frontend'), ('Backend', 'Backend'), ('App Development', 'App Devlopment'), ('Blockchain', 'Blockchain'), ('Design', 'Design'), ('Machine Learning', 'Machine Learning'), ('Artificial Intelligence', 'Artificial Intelligence')], validators=[DataRequired()])
    sub = SubmitField('Add')

db_password = os.environ.get("pswd") #input("Password for database is:")
CONNECTION_STRING = f"mongodb+srv://VIT_Admin:{db_password}@vitdiaries.tpuku.mongodb.net/CouponShare?retryWrites=true&w=majority"
print(CONNECTION_STRING)
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('Learnt!')
user_collection = pymongo.collection.Collection(db, 'Users')
add_collection = pymongo.collection.Collection(db, 'Add')
responses_collection = pymongo.collection.Collection(db, 'Responses')

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form_add = inputFormAdd()
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
                return redirect('/home')
        else:
            return redirect(url_for('home'))
    return render_template("signup.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form_add = inputFormAdd()
    form_login = inputFormlogin()
    if request.method=="POST":
        email = form_login.email.data
        pass1 = form_login.pass1.data
        if  request.method == 'POST':
            user = user_collection.find_one({"Email":email})
            print(user)
            if user == None:
                print("item is not existed")
                flash('Invalid Credentials')
                return redirect('/login')
            if check_password_hash(user['Password'], pass1):
                print("item exists")
                session['email'] = email
                return redirect('/home')
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

@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'email' not in session:
        cursor = add_collection.find()
        if request.method=="POST":
            teach = request.form.getlist("teach")
            learn = request.form.getlist("learn")
            # for i in cursor:
            #     print(i['Learn'], teach)
            #     if((i['Learn'] in teach) or (i['Teach'] in learn)):
            #         return render_template('home.html', i = i)
        return render_template('home.html', cursor=cursor)
    else:
        form_add = inputFormAdd()
        cursor = add_collection.find()
        responses = list(responses_collection.find())
        ids = []
        for response in responses:
            idx = response['postid']
            ids.append(ObjectId(idx))
        if request.method=="POST":
            can_teach = form_add.can_teach.data
            to_learn = form_add.to_learn.data
            teach = request.form.getlist("teach")
            learn = request.form.getlist("learn")
            user = user_collection.find_one({"Email":session['email']})
            if request.method=="POST":
                add_collection.insert_one({'Teach': can_teach[0], 'Learn': to_learn[0], 'Email':session['email'], 'First_Name': user['First Name'], 'Last_Name': user['Last Name']})
                return redirect(url_for('home'))
    print(ids)
    return render_template('home.html', form_add=form_add, cursor=cursor, email = session['email'], ids = ids)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('home'))
    else:
        user = user_collection.find_one({"Email":session['email']})
        reqs = list(add_collection.find({"Email":session['email']}))
        resps = list(responses_collection.find({"teacher":session['email']}))
        return render_template('profile.html', num_res = len(resps), num_reqs = len(reqs), profile_id = str(user['_id']), email= session['email'], fname = user['First Name'], lname = user['Last Name'])

@app.route('/send_request',  methods=['POST'])
def send_request():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        postid = request.form.get("postId")
        post = list(add_collection.find({"_id":ObjectId(postid)}))
        post = post[0]
        responses_collection.insert_one({"seeker":session['email'], "postid":postid, "teacher" : post['Email']})
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
