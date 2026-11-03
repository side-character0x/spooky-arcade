from flask import Flask, render_template, request, redirect
from db import Database
app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def root():
    return render_template("root.html")

@app.route("/login_initiate")
def login_initiate():
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    username=request.form["name"]
    pin=request.form["pin"]
    if Database().check_user(username,pin):
        return redirect("/home")
    else:
        return render_template("login.html", error=True)

@app.route("/signin_initiate")
def signin_initiate():
    return render_template("signin.html")

@app.route("/signin", methods=["GET","POST"])
def signin():
    username=request.form["name"]
    pin=request.form["pin"]
    verify=Database().check_username(username)
    if verify:
        Database().add_user(username,pin)
        return redirect("/home")
    else:
        return render_template("signin.html",error=True)


app.run(debug=True)