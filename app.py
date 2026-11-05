from flask import Flask, render_template, request, redirect, session
from db import Database
import random

app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def root():
    return render_template("gamble.html")

@app.route("/login_initiate")
def login_initiate():
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    username=request.form["name"]
    pin=request.form["pin"]
    if Database().check_user(username,pin):
        session["username"]=username
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
        session["username"]=username
        return redirect("/home")
    else:
        return render_template("signin.html",error=True)

@app.route("/home")
def home():
    username=session["username"]
    candies=Database().get_candies(username)
    return render_template("home.html",username=username, candies=candies)

@app.route("/route")
def route():
    username=session['username']
    candies=Database().get_candies(username)
    return render_template("route.html", username=username, cnadies=candies)

@app.route("/gamble")
def gamble():
    return render_template("/gamble.html")

@app.route("/pregamble", methods=["GET","POST"])
def pregamble():
    if request.method=="POST":
        difficulty=request.form["difficulty"]
        if difficulty=="easy":
            session["candies"]=[1,1,1,4]
        elif difficulty=="medium":
            session["candies"]=[1,1,2,4]
        elif difficulty=="hard":
            session["candies"]=[1,1,3,4]
        elif difficulty=="extreme":
            session["candies"]=[1,2,3,4]
        return redirect("/gambleset")
    return render_template("pregamble.html")

@app.route("/gambleset")
def gambleset():
    candies=session["candies"]
    random.shuffle(candies)
    session["candies_order"]=candies
    session["pot_candies"]=20
    return redirect("/gamblegame")

@app.route("/gamblegame", methods=["GET","POST"])
def gamblegame():
    if request.method=="POST":
        # if session["pot_candies"]<=0:
        #     return render_template("gamble_over.html")
        cashout=request.form.get("cashout")
        if cashout:
            pass                                 #incomplete
        box=int(request.form.get("box"))
        candy=session["candies_order"][box-1]
        if candy==1:
            session["pot_candies"]*=2
            pot_candies=session["pot_candies"]
            return render_template("golden_candy.html", pot_candies=pot_candies)
        elif candy==2:
            pot_candies=session["pot_candies"]
            return render_template("empty_box.html", pot_candies=pot_candies)
        elif candy==3:
            session["pot_candies"]-=10
            pot_candies=session["pot_candies"]
            return render_template("normal_candy.html", pot_candies=pot_candies)
        elif candy==4:
            session["pot_candies"]=0
            return render_template("cursed_candy.html")
    return render_template("gamblegame.html")

app.run(debug=True)