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
import numpy as np
from boto3.s3.transfer import S3Transfer
from boto.s3.connection import S3Connection
import boto
import boto3
import boto.s3
from boto.s3.key import Key 
import pickle
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
import bokeh
from bokeh import *
from bokeh.embed import components
from werkzeug.utils import secure_filename
import base64
import urllib.request
app = Flask(__name__)
app.secret_key = 'Shantanu06'
#mysql = MySQL()
# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
#app.config['MYSQL_DATABASE_DB'] = 'crimesinchicago'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)
#conn = mysql.connect()
#cursor = conn.cursor()
S3_KEY = "AKIAI6BF5SDIVG5M3FIA"
S3_SECRET_ACCESS_KEY = "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"
S3_BUCKET = "assignment3adsteam8"
url = "https://s3.amazonaws.com/adsfinalproject/Chicago_Crimes_2012_to_2017.csv"
urllib.request.urlretrieve(url, 'Chicago_Crimes_2012_to_2017.csv')
crimes = pd.read_csv('Chicago_Crimes_2012_to_2017.csv' , error_bad_lines = False )
conn = S3Connection(S3_KEY, S3_SECRET_ACCESS_KEY)
b = conn.get_bucket(S3_BUCKET)
for obj in b.get_all_keys():
    trial = obj.get_contents_to_filename(obj.key)
#feature_names = crimes.columns[:].values.tolist()
#crimes.Date = pd.to_datetime(crimes.Date, format='%m/%d/%Y %I:%M:%S %p')  
#crimes.index = pd.DatetimeIndex(crimes.Date)
@app.route("/")
def main():
    return render_template("index.html")
@app.route("/graph/", methods=["POST"])
def graph():
    

    crimes.Date = pd.to_datetime(crimes.Date, format='%m/%d/%Y %I:%M:%S %p')  
    crimes.index = pd.DatetimeIndex(crimes.Date)
    if(request.form['EDA'] == "Primary Type"):
        plt.figure(figsize=(8,10))
        crimes.groupby([crimes['Primary Type']]).size().sort_values(ascending=True).plot(kind='barh')
        plt.title('Number of crimes by type')
        plt.ylabel('Crime Type')
        plt.xlabel('Number of crimes')
        
        img = io.BytesIO()
        img.seek(0)
        plt.savefig(img, format='png')
        plot_url = base64.b64encode(img.getvalue()).decode()

        return '<img src="data:image/png;base64,{}">'.format(plot_url)


    elif(request.form['EDA'] == "Month"):
        crimes.groupby([crimes.index.month]).size().plot(kind='barh')
        plt.ylabel('Months')
        plt.xlabel('Number of crimes')
        plt.title('Number of crimes by Month ')
        
        img = io.BytesIO()
        img.seek(0)
        plt.savefig(img, format='png')
        plot_url = base64.b64encode(img.getvalue()).decode()

        return '<img src="data:image/png;base64,{}">'.format(plot_url)

    elif(request.form['EDA'] == "Week"):
        days = ['Monday','Tuesday','Wednesday',  'Thursday', 'Friday', 'Saturday', 'Sunday']
        crimes.groupby([crimes.index.dayofweek]).size().plot(kind='barh')
        plt.figure(figsize=(11,5))
        plt.ylabel('Days of the week')
        plt.yticks(np.arange(7), days)
        plt.xlabel('Number of crimes')
        plt.title('Number of crimes by day of the week')
        img = io.BytesIO()
        img.seek(0)
        plt.savefig(img, format='png')
        plot_url = base64.b64encode(img.getvalue()).decode()

        return '<img src="data:image/png;base64,{}">'.format(plot_url)
    elif(request.form['EDA'] == "Location Description"):
        plt.figure(figsize=(8,10))
        crimes.groupby([crimes['Location Description']]).size().sort_values(ascending=True).plot(kind='barh')
        plt.title('Number of crimes by Location')
        plt.ylabel('Crime Location')
        plt.xlabel('Number of crimes')
        
        img = io.BytesIO()
        img.seek(0)
        plt.savefig(img, format='png')
        plot_url = base64.b64encode(img.getvalue()).decode()

        return '<img src="data:image/png;base64,{}">'.format(plot_url)
    elif(request.form['EDA'] == "cpm1"):


        img = io.BytesIO()
        plt.figure(figsize=(11,5))
        crimes_count_date = crimes.pivot_table('ID', aggfunc=np.size, columns='Primary Type', index=crimes.index.date, fill_value=0)
        crimes_count_date.index = pd.DatetimeIndex(crimes_count_date.index)
        plo = crimes_count_date.rolling(365).sum().plot(figsize=(12, 30), subplots=True, layout=(-1, 3), sharex=False, sharey=False)
        plt.xticks(rotation = 90)
        #plt.title('Crimes Seperated by types and its occurance in the years')
        plt.savefig(img, format='png')
        img.seek(0)

        plot_url = base64.b64encode(img.getvalue()).decode()

        return '<img src="data:image/png;base64,{}">'.format(plot_url)
    elif(request.form['EDA'] == "cpm"):
        plt.figure(figsize=(11,5))
        img = io.BytesIO()
        crimes.resample('M').size().plot(legend=False)
        plt.title('Crime Rate Per Year (2008 - 2016)')
        plt.xlabel('Months')
        plt.ylabel('Number of crimes')
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return '<img src="data:image/png;base64,{}">'.format(plot_url)

@app.route('/showSignUp/')
def showSignUp():
    return render_template('signup.html')
@app.route('/showSignin/')
def showSignin():
    return render_template('signup.html')  
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
        name = request.form['inputName']
        password_form  = request.form['inputPassword']
        if(username_form == "admin" and password_form == "admin"):
            #print(data)
            return render_template("loggedin.html", name=name)
       
        else:
            flash("Ops! Wrong Credentials")
            return render_template("signup.html" )
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
        lr_Model = pickle.load(open('lr_model.pckl', 'rb'))
        #bnb_Model = pickle.load(open('bnb_model.pckl', 'rb'))
        prediction2 = lr_Model.predict(var)
        #prediction3 = bnb_Model.predict(var)
        return render_template('predicted_form.html', beat_Count = beat_Count, prediction2= prediction2)
    else:
            flash("Something went wrong")
            return render_template("fill_form.html")
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
        try:
            file_path = os.path.join(dir_name, filename)
            file.save(file_path)
            dataset = pd.read_csv(file_path)
            print("Data Read")
            return render_template('predicted_CSV.html')
        except:
            flash("Please Upload only CSV file")
            return render_template('upload_csv.html')
    return render_template('upload_csv.html')         
def create_fig(current_feature_name,bins):
    p = Histogram(crimes, current_feature_name, title='Primary_Type', 
    bins=bins, legend='top_right', width=600, height=400)
    # Set the x axis label
    p.xaxis.axis_label = current_feature_name
    # Set the y axis label
    p.yaxis.axis_label = 'Count'
    return p

@app.route('/graph1/', methods=["POST"])
def graph1():
    current_feature_name = request.args.get("feature_name")
# Create the plot
    plot = create_fig(current_feature_name, 10)
    
# Embed plot into HTML via Flask Render
    script, div = components(plot)
    return render_template("trial.html", script=script, div=div,
        feature_names=feature_names,  current_feature_name=current_feature_name)
   
if __name__ == "__main__":

#app.debug = True
    app.run()	