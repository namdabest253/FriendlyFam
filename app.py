"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import gunicorn

app.secret_key = "My Secret"


db = mysql.connector.connect(
    host="us-cdbr-east-03.cleardb.com",
    user="b5af5cea72b983",
    password="78f442bb",
    database="heroku_c3809d5db01c0cd"
    )

cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), password VARCHAR(50))")
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, host VARCHAR(100), description VARCHAR (255), day VARCHAR (50), time VARCHAR(20), status VARCHAR(20))")
db.commit


@app.route('/')
def index():
    if "username" in session:
        sql = "SELECT host, description, day, time, status, FROM events"
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results) == 0:
            return render_template("/home.html", user = session["username"])
        else:
            return render_template("/home.html", user = session["username"], list=results)
    else:
        return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        description = request.form.get("description")
        day = request.form.get("day")
        time = request.form.get("time")
        sql = "INSERT INTO events(host, description, day, time, status) VALUES(%s, %s, %s, %s, 'Scheduled')"
        values = (session["username"], description, day, time)
        cursor.execute(sql, values)
        db.commit()
        return redirect("/myevents")
    else:
        return render_template("add.html", user = session["username"])

@app.route("/myevents")
def myEvents():
    sql = "SELECT host, description, day, time, status FROM events WHERE host = %s"
    values = (session["username"])
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if len(result) == 0:
        return render_template("myevents.html", user = session["username"])
    else:
        return render_template("myevents.html", user-session["username"])



if __name__ == '__main__':
    app.run()
