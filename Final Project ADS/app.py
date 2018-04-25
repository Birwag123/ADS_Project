from flask import Flask, render_template, json, request, flash,session, make_response, Markup, send_file
from flask.ext.mysql import MySQL
from hashlib import *
import pandas as pd
from werkzeug import generate_password_hash, check_password_hash
from passlib.hash import sha256_crypt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import datetime as dt
import io
import os
import plotly
import json
import pandas as pd
import plotly.plotly as py
from ipywidgets import widgets 
from IPython.display import display
from plotly.graph_objs import *
from plotly.widgets import GraphWidget
import pygal
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = 'Shantanu06'
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'crimesinchicago'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
crimes = pd.read_csv('F:/Chicago_Crimes_2012_to_2017.csv' , error_bad_lines = False)
print("Data Read")  
#crimes.Date = pd.to_datetime(crimes.Date, format='%m/%d/%Y %I:%M:%S %p')  
#crimes.index = pd.DatetimeIndex(crimes.Date)
@app.route("/")
def main():
    return render_template("index.html")
@app.route("/graph/", methods=["POST"])
def graph():
    crimes.Date = pd.to_datetime(crimes.Date, format='%m/%d/%Y %I:%M:%S %p')  
    crimes.index = pd.DatetimeIndex(crimes.Date)

    #crimes['Date'] = pd.to_datetime(crimes['Date'])
    #crimes['Day']=crimes['Date'].dt.weekday_name
    #print("day")
    #crimes['Hour']=crimes['Date'].dt.hour
    #print("hour")
    #crimes['Month']=crimes['Date'].dt.month
    #print("month")
    #crimes['Year'] = crimes['Date'].dt.year
    #print("year")
    
    if(request.form['EDA'] == "Primary Type"):
        line_chart = pygal.HorizontalBar()
        line_chart.title = 'Primary Type'
        line_chart.add('Primary Type', crimes.groupby([crimes['Primary Type']]).size().sort_values(ascending=True))
        graph_data = line_chart.render_data_uri()
        return render_template('graph1.html',  graph_data=graph_data)

    elif(request.form['EDA'] == "Location Description"):
        print("BILL_AMT2")
        graphs = [
        dict(
            data=[
                dict(
                    x =  crimes.groupby([crimes['Location Description']]).size().sort_values(ascending=True),
                    type='bar'
                ),
            ],
            layout=dict(
                title='first graph'
            )
            )]

        ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)] 
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graph.html', 
                           ids=ids,
                           graphJSON=graphJSON)

    elif(request.form['EDA'] == "Week"):
        line_chart = pygal.HorizontalBar()
        line_chart.title = 'Number of Crimes by day of the week' 
        line_chart.add('Week', crimes.groupby([crimes.index.dayofweek]).size())
        graph_data = line_chart.render_data_uri()
        return render_template('graph1.html',  graph_data=graph_data)
    elif(request.form['EDA'] == "Month"):
        line_chart = pygal.HorizontalBar()
        line_chart.title = 'Number of Crimes by day of the Month' 
        line_chart.add('Month', crimes.groupby([crimes.index.month]).size())
        graph_data = line_chart.render_data_uri()
        return render_template('graph1.html',  graph_data=graph_data)

@app.route('/showSignUp/')
def showSignUp():
    return render_template('signup.html')
@app.route('/showSignin/')
def showSignin():
    return render_template('signin.html')  
@app.route('/showSignOut/', methods=['POST'])
def signOut():
    session.pop('username_form')
    flash("You are Successfully Logged Out")
    return render_template('signin.html')          	
@app.route('/signUp/',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    _name = request.form['inputName']
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    cursor.callproc('Create_New_User',(_name,_username,_password))
    data = cursor.fetchall()
 
    if len(data) is 0:
        conn.commit()
        flash('Welcome! Please Sign In to proceed')    
        return render_template('signup.html')  
        session['logged_in'] = True
        session['_username']  

    else:
        flash('Ops! Username Exists')
        return render_template('signup.html')

@app.route('/signIn/', methods=["GET","POST"])
def signIn():

    if request.method == "POST":

        username_form  = request.form['inputEmail']
        password_form  = request.form['inputPassword']
        data = cursor.execute("SELECT * FROM user WHERE user_username  = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
        #print(data)
        data = cursor.fetchone()[3]
        data1 = cursor.execute("SELECT * FROM user WHERE user_username  = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
        data1 =cursor.fetchone()[1]
        print(data1)
        if(password_form == data):
            #print(data)
            session['Logged in'] = True
            username = session['username_form'] = request.form['inputEmail']
            session['user_username'] = data1
            return render_template("loggedin.html", data1=data1)
       
        else:
            flash("Ops! Wrong Credentials")
            return render_template("signin.html" )
@app.route('/fill_form/', methods=['POST'])
def fill_form():
    if request.method== "POST":
        username = session['user_username']
        locationd = crimes['Location Description'].unique()   
        return render_template('fill_form.html',username = username, locationd = locationd)
    else:
        return render_template('loggedin.html')
@app.route("/upload_csv/", methods = ["POST"])
def upload_csv():
    if request.method == "POST":
        return render_template("upload_csv.html")
    else: 
        return render_template("loggedin.html")
@app.route('/prediction_form/', methods=['POST'])
def prediction_form():
    if request.method == "POST":
        if(request.form['District'] == "1"):
            beat_Count = "19"
        elif(request.form['District'] == "2"):
            beat_Count = "29"
        elif(request.form['District'] == "3"):
            beat_Count = "17"
        elif(request.form['District'] == "4"):
            beat_Count = "14"
        elif(request.form['District'] == "5"):
            beat_Count = "10"
        elif(request.form['District'] == "6"):
            beat_Count = "17"
        elif(request.form['District'] == "7"):
            beat_Count = "20"
        elif(request.form['District'] == "8"):
            beat_Count = "17"
        elif(request.form['District'] == "9"):
            beat_Count = "23"
        elif(request.form['District'] == "10"):
            beat_Count = "15"
        elif(request.form['District'] == "11"):
            beat_Count = "19"
        elif(request.form['District'] == "12"):
            beat_Count = "36"
        elif(request.form['District'] == "14"):
            beat_Count = "16"
        elif(request.form['District'] == "15"):
            beat_Count = "13"
        elif(request.form['District'] == "16"):
            beat_Count = "23"
        elif(request.form['District'] == "17"):
            beat_Count = "10"
        elif(request.form['District'] == "18"):
            beat_Count = "17"
        elif(request.form['District'] == "19"):
            beat_Count = "29"
        elif(request.form['District'] == "20"):
            beat_Count = "11"
        elif(request.form['District'] == "22"):
            beat_Count = "15"
        elif(request.form['District'] == "24"):
            beat_Count = "10"
        elif(request.form['District'] == "25"):
            beat_Count = "18"
        Primary_Type = request.form['Crime_Type']
        Primary_Type = int(Primary_Type)
        Ward = request.form['ward']
        Ward = float(Ward)
        District = request.form['District']
        District = float(District)
        Community = request.form['Community']
        Community = float(Community)
        X = [[Primary_Type , Ward , District , Community ]]
        var = pd.DataFrame(X)
        print(var)
        return render_template('predicted_form.html', beat_Count = beat_Count)
    else:
            return "OPS"
@app.route('/Prediction_CSV/' ,methods= ['POST'])
def Prediction_CSV():
        # A
    if "filename" not in request.files:
        return "No user_file key in request.files"

    # B
    file = request.files["filename"]

    # C.
    if file.filename == "":
        return "Please select a file"

    # D.
    if file:    
        
        filename = secure_filename(file.filename)
        dir_name = 'uploads/'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_path = os.path.join(dir_name, filename)
        file.save(file_path)
    try:
        dataset = pd.read_csv(file_path)
        print("Data Read")
        return render_template('predicted_CSV.html')
    except:
        return "Please Select Only CSV File"
   


if __name__ == "__main__":

#app.debug = True
    app.run()	