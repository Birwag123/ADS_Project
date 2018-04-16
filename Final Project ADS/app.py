from flask import Flask, render_template, json, request, flash,session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'Shantanu06'

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'crimesinchicago'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
def main():
    return render_template("index.html")
	
@app.route('/showSignUp/')
def showSignUp():
    return render_template('signup.html')	
@app.route('/signUp/',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _hashed_password = generate_password_hash(_password)

    conn = mysql.connect()
    cursor = conn.cursor()
	
    cursor.callproc('Create_New_User',(_name,_email,_hashed_password))
	
    # validate the received values

    data = cursor.fetchall()
 
    if len(data) is 0:
        conn.commit()
        flash('Welcome! Please Sign In to proceed')    
        return render_template('signup.html')    

    else:
        flash('Ops! Username Excits')
        return render_template('signup.html')

				
if __name__ == "__main__":

#app.debug = True
    app.run()	