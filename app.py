from flask import Flask, render_template, request, redirect, session
import mysql.connector
import gunicorn
#from flask_wtf.csrf import CSRFPROTECT

app = Flask(__name__)
app.secret_key = "My Secret"

#csrf = CSRFProtect()
#csrf.innit_app(app)

db = mysql.connector.connect(
    host="us-cdbr-east-03.cleardb.com",
    user="b9f64af02f7048",
    password="d2e56239",
    database="heroku_85063ffbb3a4c24"
    )

cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), password VARCHAR(50))")
#Looks like you are creating the users table twice - change this one to "events"
cursor.execute("CREATE TABLE IF NOT EXISTS events (id INT AUTO_INCREMENT PRIMARY KEY, host VARCHAR(100), description VARCHAR (255), day VARCHAR (50), time VARCHAR(20), status VARCHAR(20))")
db.commit()


@app.route("/")
def index():
    if "username" in session:
        sql = "SELECT host, description, day, time, status FROM events"
        cursor.execute(sql)
        results = cursor.fetchall()
        #No forward slash needed when we render home.html!
        if len(results) == 0:
            return render_template("home.html", user = session["username"])
        else:
            return render_template("home.html", user = session["username"], list=results)
    else:
        return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
      username = request.form.get("username")
      password = request.form.get("password")
      
      sql = "SELECT username FROM users WHERE username = %s AND password = %s";
      value = (username, password)
      cursor.execute(sql, value)

      result = cursor.fetchall()

      if len(result) > 0:
          session["username"] = username
          return redirect("/")
      else:
          return render_template("home.html", error = "Invalid Username or Password")
  else:
      return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form["confirm-password"]
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        sql = "SELECT username FROM users WHERE username = %s";
        value = (username,)
        cursor.execute(sql, value)
        result = cursor.fetchall()
        if len(result) > 0:
            return render_template("signup.html", error="Username already exists")
        else:
            sql = "INSERT INTO users(username, password) VALUES (%s, %s)"
            values =[username,password]
            cursor.execute(sql, values)
            db.commit()
        session["username"] = username
        return redirect("/")
    else:
        return render_template("signup.html")



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

#Double check this route, you don't appear to be using your results variable
@app.route("/myevents")
def myEvents():
    sql = "SELECT host, description, day, time, status FROM events WHERE host = %s"
    values = (session["username"])
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if len(result) == 0:
        return render_template("myevents.html", user = session["username"])
    else:
        #user-session is probably meant to be user = session!
        return render_template("myevents.html", user = session["username"])

@app.route("/cancel/<int:id>")
def editEvent(id):
    sql = "UPDATE events SET status = 'Cancelled' WHERE id = %s"
    values = (id,)
    cursor.execute(sql, values)
    db.commit()
    return redirect("/myevents")

@app.route("/update/<int:id>", methods = ["GET", "POST"])
def updateEvent(id):
    sql = "SELECT id, host, description, day, time, status FROM events WHERE id = %s"
    values = (id,)
    cursor.execute(sql, values)
    result = cursor.fetchone()
    if request.method == "POST":
        username = session["username"]
        description= request.form.get("description")
        day = request.form.get("day")
        time = request.form.get("time")
        status = request.form.get("status")
        sql = "UPDATE events SET description = %s, day = %s, time = %s, status = %s WHERE id = %s"
        values = (description, day, time, status, id)
        cursor.execute(sql, values)
        db.commit()
        return redirect("/myevents")
    else:
        return render_template("edit.html", user = session["username"], event = result)

if __name__ == '__main__':
    app.run()
