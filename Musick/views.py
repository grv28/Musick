from flask import Flask, render_template, request, redirect, url_for,session
from flask_login import login_required
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import numpy as np
import pandas as pd
from flask import *  
import os

app=Flask(__name__)
app.secret_key = 'AAbb'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jagrit'
app.config['MYSQL_DB'] = 'musick'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/About_us')
def about_us():
    return render_template("About_Us.html")

@app.route('/login',methods = ["GET","POST"])
def login():
     msg = ''
     if request.method == 'POST' and 'Uname' in request.form and 'Pass' in request.form:
        uname = request.form['Uname']
        pas = request.form['Pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE Email = %s AND Password = %s', (uname, pas))
        account = cursor.fetchone()
        print(account)
        if account:
            if((uname=='admin@admin.com')and(pas=='admin')):  
                        session['loggedin'] = True
                        session['Email'] = account['Email']
                        session['Password'] = account['Password']
                        return redirect(url_for("admin"))
            else:
                session['userlogin'] = True
                session['username']= account['Username']
                session['Email'] = account['Email']
                session['Password'] = account['Password']
                return redirect(url_for("choice",username=session['username']))
        else:
            msg = 'Incorrect username/password!'
     return render_template('Login.html',msg=msg)


@app.route('/404')
def error():
     return render_template('404.html')


@app.route('/admin')
def admin():
    if 'loggedin' in session:
        return render_template('admin_index.html')
    return redirect(url_for('error'))


@app.route('/register')
def register():
    return render_template('Register.html')


@app.route('/svereg',methods = ["POST","GET"])
def saveDetails():
    msg=""
    if request.method == "POST":    
            uid=request.form['uid']
            name=request.form['name']
            email=request.form['email']
            pas=request.form['pass']
            con=request.form['contact']
 
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO login (Username,Email,Password) VALUES (%s,%s,%s) ', (uid,email,pas))
                cursor.execute('INSERT INTO post (Username,Video) VALUES (%s,%s) ', (uid,'default.mp4'))
                cursor.execute('INSERT INTO info(Username,Full_Name,Contact,dp) VALUES (%s, %s, %s, %s)', (uid,name,con,'default.png'))
                cursor.execute('INSERT INTO location(Username,location) VALUES (%s, %s)', (uid,""))
                msg = "Registered Successfully"  
                mysql.connection.commit()
                cursor.close()
                return render_template("sucess.html",msg = msg) 
                
            except:
                msg="Username already in use"
                return render_template("sucess.html",msg = msg)



@app.route('/user/choice/<username>')
def choice(username):
    if 'userlogin' in session:
        return render_template("Choice.html",username=username)

@app.route('/view',methods=["GET","POST"])
def view():
 
    if 'userlogin' in session:
       
        if request.method == "POST":

             if request.form.get('artist') == 'Artist':
                print("Artist")
                return redirect(url_for("artist"))
             else:
                print("Composer")
                return redirect(url_for("composer"))


    return redirect(url_for("choice",username=session['username']))



@app.route('/artist/view')
def artist():
    if 'userlogin' in session:
            username=session['username']
            email=session['Email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT info.dp FROM info WHERE info.username= %s',(username,))
            fname=cursor.fetchone()
            fname = fname['dp']
            cursor.execute('SELECT info.Full_name FROM info WHERE info.username= %s',(username,))
            fullname=cursor.fetchone()
            fullname=fullname['Full_name']
            cursor.execute('SELECT loaction FROM location WHERE Username= %s',(username,))
            location=cursor.fetchone()
            location=location['loaction']
            cursor.execute('SELECT aboutme FROM location WHERE Username= %s',(username,))
            aboutme=cursor.fetchone()
            aboutme=aboutme['aboutme']
            cursor.execute('SELECT COUNT(*) FROM post WHERE Username= %s',(username,))
            i=cursor.fetchone()
            i=i['COUNT(*)']
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT post.Video FROM post WHERE post.username= %s',(username,))
            pname=cursor.fetchall()
            cursor.close()
            return render_template('artistview.html',name=username,fname=fname,fullname=fullname,i=i,pname=pname,email=email,location=location,aboutme=aboutme)

@app.route('/deletepost', methods=["POST","GET"])
def deletepost():
     if 'userlogin' in session:  
       un=session['username']
       if request.method == 'POST':
            file=request.values.get("delete")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM post WHERE Video = %s and Username= %s', (file,un))
            mysql.connection.commit()
            cursor.close()

       return redirect(url_for("artist",username=un))


@app.route('/newpost',methods=["GET","POST"])
def createpost():
    if 'userlogin' in session:
          un=session['username']
          if request.method == "POST" :
            f = request.files['postfile']  
            f.save('static/post_images/'+un+f.filename)
            print(f)
            print("before")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO post(Username,Video) VALUES(%s,%s)', (un,un+f.filename))
            mysql.connection.commit()
            cursor.close()
            print(f)
            return redirect(url_for("artist",username=un))
          
    return render_template("upload.html")



@app.route('/edit',methods = ["POST","GET"])
def edit():
    username=session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT login.Email,info.Username,info.Full_Name,info.dp,info.Contact FROM login,info WHERE login.Username=info.Username and login.username= %s',(username,))
    data=cursor.fetchall()
    display=data[0]['dp']
    cursor.execute('SELECT loaction FROM location WHERE Username= %s',(username,))
    location=cursor.fetchone()
    location=location['loaction']
    cursor.execute('SELECT aboutme FROM location WHERE Username= %s',(username,))
    aboutme=cursor.fetchone()
    aboutme=aboutme['aboutme']
    cursor.close()
    if request.method == "POST":    
        un=request.form['uname']
        name=request.form['name']
        contact=request.form['contact']
        location=request.form['location']
        aboutme=request.form['aboutme']
        f = request.files['file']  
        f.save('static/user_images/'+un+f.filename)
        if 'file' in request.files:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE info SET Full_name= %s ,Contact= %s, dp= %s WHERE Username= %s', (name,contact,un+f.filename,un))       
            cursor.execute('UPDATE location set loaction= %s WHERE Username= %s', (location,un))
            cursor.execute('UPDATE location set aboutme= %s WHERE Username= %s', (aboutme,un))
            mysql.connection.commit()   
            cursor.close()
            return redirect(url_for("artist",username=un))
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE info SET Full_name= %s ,Contact= %s WHERE Username= %s', (name,contact,un))       
            cursor.execute('UPDATE location set loaction= %s WHERE Username= %s', (location,un))
            cursor.execute('UPDATE location set aboutme= %s WHERE Username= %s', (aboutme,un))
            mysql.connection.commit()   
            cursor.close()
            return redirect(url_for("artist",username=un))

    return render_template("edit.html",data=data,location=location,aboutme=aboutme)



@app.route('/comp/view')
def composer():
     if 'userlogin' in session:
         username=session['username']
         email=session['Email']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT info.dp FROM info WHERE info.username= %s',(username,))
         fname=cursor.fetchone()
         fname = fname['dp']
         cursor.execute('SELECT info.Full_name FROM info WHERE info.username= %s',(username,))
         fullname=cursor.fetchone()
         fullname=fullname['Full_name']
         cursor.execute('SELECT COUNT(*) FROM post WHERE Username= %s',(username,))
         i=cursor.fetchone()
         i=i['COUNT(*)']
         cursor.execute('SELECT loaction FROM location WHERE Username= %s',(username,))
         location=cursor.fetchone()
         location=location['loaction']
         cursor.close()
         return render_template('composerview.html',name=username,fname=fname,fullname=fullname,i=i,location=location,email=email)

@app.route('/viewartists')
def viewartists():
     if 'userlogin' in session:
         username=session['username']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute("SELECT * from info ")
         details=cursor.fetchall()
         print(details)

         cursor.close()
         return render_template('artists.html',details=details)
   
     

@app.route('/artistselect')
def selection():
     if 'userlogin' in session:
         username=session['username']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute("SELECT * from info ")
         details=cursor.fetchall()
         print(details)

         cursor.close()
         return render_template('artistselect.html',details=details)
    





@app.route('/logout')
def logout():
   if 'loggedin' in session:
    session.pop('loggedin', None)
    session.pop('uname', None)
    session.pop('pas', None)
    return redirect(url_for('login'))

   else:
        session.pop('userlogin', None)
        session.pop('uname', None)
        session.pop('pas', None)
        return redirect(url_for('login'))
   return redirect(url_for('error'))

if __name__ == '__main__':
    app.run(debug=True)
