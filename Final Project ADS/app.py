from flask import Flask, render_template, json, request, flash,session, make_response, Markup
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
import plotly
import json
import pandas as pd
import plotly.plotly as py
from ipywidgets import widgets 
from IPython.display import display
from plotly.graph_objs import *
from plotly.widgets import GraphWidget

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
@app.route("/")
def main():
    return render_template("index.html")
@app.route("/graph/", methods=["POST"])
def graph():
    crimes = pd.read_csv('F:/Chicago_Crimes_2008_to_2011.csv' , error_bad_lines = False)
    print("Data Read")    
    crimes['Date'] = pd.to_datetime(crimes['Date'])
    crimes['Day']=crimes['Date'].dt.weekday_name
    print("day")
    crimes['Hour']=crimes['Date'].dt.hour
    print("hour")
    crimes['Month']=crimes['Date'].dt.month
    print("month")
    crimes['Year'] = crimes['Date'].dt.year
    print("year")
    
    if(request.form['graph'] == "Year"):
        print("LIMIT_BAL")


        graphs = [
        dict(
            data=[
                dict(
                    x= crimes['Year'],
                    y= crimes.groupby([crimes['Primary Type']]).size().sort_values(ascending=True),
                    type='bar'
                ),
            ],
            layout=dict(
                title='first graph'
            )
            )]
    elif(request.form['graph'] == "BILL_AMT2"):
        print("BILL_AMT2")
        graphs = [
        dict(
            data=[
                dict(
                    x= crimes['ID'],
                    y= crimes['BILL_AMT2'],
                    type='bar'
                ),
            ],
            layout=dict(
                title='first graph'
            )
            )]

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)] 
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('login.html',
                           ids=ids,
                           graphJSON=graphJSON)    

@app.route('/showSignUp/')
def showSignUp():
    return render_template('signup.html')
@app.route('/showSignin/')
def showSignin():
    return render_template('signin.html')        	
@app.route('/signUp/',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    _name = request.form['inputName']
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']



	
    cursor.callproc('Create_New_User',(_name,_username,_password))
	
    # validate the received values

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
        #print(data)
        if(password_form == data):
            #print(data)
            session['Logged in'] = True
            session['username_form'] = request.form['inputEmail']
            return render_template("login.html")
       
        else:
            flash("Ops! Wrong Credentials")
            return render_template("signin.html" )
@app.route('/plot.png/' , methods= ['POST'])
def plot():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]

    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    c = canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return render_template("login.html" , c=c)


if __name__ == "__main__":

#app.debug = True
    app.run()	