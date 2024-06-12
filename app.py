import sys, os
from signLanguage.pipeline.training_pipeline import TrainPipeline
from signLanguage.exception import SignException
from signLanguage.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template,Response,redirect, url_for,session,flash
from flask_cors import CORS, cross_origin

from dbconnection.connection import register_user,validate_login

import secrets
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
#CORS(app)
# Database configuration
'''app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sign_language:saurav@localhost/sign_language'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)'''



class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"

'''class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)'''

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about.html")
def about():
    return render_template("about.html")
#Protect Route that require Authenticaton
# Ensure that only logged-in users can access certain routes.
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/make_prediction.html")
@login_required
def make_prediction():
    return render_template("make_prediction.html")

@app.route("/index.html")
def index():
    return render_template("index.html")



@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if validate_login(email, password) == 1:
            # Set session data
            session['logged_in'] = True
            session['email'] = email
            # Redirect to a dashboard or home page after successful login
            return render_template('home.html')
        else:
            # Show an error message and redirect to login page
            flash('User not found / Incorrect email or password')
            return render_template("login.html")
    else:
        return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username= str(request.form.get('username'))
        email= str(request.form.get('email'))
        password= str(request.form.get('password'))
        age= int(request.form.get('age'))
        confirm_pass=str(request.form.get('confirm_password'))

        if password !=confirm_pass:
            flash("Passwords do not match")
            return render_template('register.html')
        else:
        #now storing these information inside our database
            register_user(username,age,email,confirm_pass)
            return render_template('login.html')
    else:
        return render_template('register.html')


'''@app.route("/register.html", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login.html"))'''




@app.route("/train")
def trainRoute():
    obj = TrainPipeline()
    obj.run_pipeline()
    return "Training Successfull!!" 




@app.route("/predict", methods=['POST','GET'])
@cross_origin()
def predictRoute():
    try:
        image = request.json['image']
        decodeImage(image, clApp.filename)

        os.system("cd yolov5/ && python detect.py --weights my_model.pt --img 416 --conf 0.5 --source ../data/inputImage.jpg")

        opencodedbase64 = encodeImageIntoBase64("yolov5/runs/detect/exp/inputImage.jpg")
        result = {"image": opencodedbase64.decode('utf-8')}
        os.system("rm -rf yolov5/runs")

    except ValueError as val:
        print(val)
        return Response("Value not found inside  json data")
    except KeyError:
        return Response("Key value error incorrect key passed")
    except Exception as e:
        print(e)
        result = "Invalid input"

    return jsonify(result)




@app.route("/live", methods=['GET'])
@cross_origin()
def predictLive():
    try:
        os.system("cd yolov5/ && python detect.py --weights my_model.pt --img 416 --conf 0.5 --source 0")
        os.system("rm -rf yolov5/runs")
        return "Camera starting!!" 

    except ValueError as val:
        print(val)
        return Response("Value not found inside  json data")
    



if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host="0.0.0.0", port=5000,debug=True)
