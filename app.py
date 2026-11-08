from flask import Flask, render_template, request, redirect, session
from db import Database
import random
from candies import CANDY_TYPES
from monsters import Monster_clues, Monsters
from questions import Questions

app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def root():
    return render_template("guess.html")

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
    return render_template("route.html", username=username, candies=candies, eligibility=True)

@app.route("/gamble")
def gamble():
    candies=Database().get_candies(session["username"])
    if candies<30:
        username=session['username']
        candies=Database().get_candies(username)
        return render_template("route.html", username=username, candies=candies, eligibility=False)
    Database().reduce_candies(session["username"],30)
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
    session["pot_candies"]=30
    return redirect("/gamblegame")

@app.route("/cashout")
def cashout():
    username=session["username"]
    pot_candies=session["pot_candies"]
    session["pot_candies"]=0
    Database().add_candies(username,pot_candies)
    current_balance=Database().get_candies(username)
    return render_template("cashout.html", current_balance=current_balance, cashed_candy=pot_candies)

def gambleview(url):
    candies=session["candies_order"]
    box_1=CANDY_TYPES[str(candies[0])]
    box_2=CANDY_TYPES[str(candies[1])]
    box_3=CANDY_TYPES[str(candies[2])]
    box_4=CANDY_TYPES[str(candies[3])]
    return render_template("gamble_view.html", pot_candies=session["pot_candies"],box_1=box_1, box_2=box_2, box_3=box_3, box_4=box_4,url=url)

@app.route("/gamblegame", methods=["GET","POST"])
def gamblegame():
    if request.method=="POST":
        random.shuffle(session["candies_order"])
        if session["pot_candies"]<=0:
            return render_template("gamble_over.html")
        cashout=request.form.get("cashout")
        if cashout:
            return redirect("/cashout")
        box=int(request.form.get("box"))
        candy=session["candies_order"][box-1]
        if candy==1:
            return gambleview("/golden")
        elif candy==2:
            return gambleview("/empty")
        elif candy==3:
            return gambleview("/normal")
        elif candy==4:
            return gambleview("/cursed")
    return render_template("gamblegame.html",pot_candies=session["pot_candies"])

@app.route("/golden")
def golden_candy():
    session["pot_candies"]*=2
    pot_candies=session["pot_candies"]
    return render_template("golden_candy.html", pot_candies=pot_candies)

@app.route("/empty")
def empty():
    pot_candies=session["pot_candies"]
    return render_template("empty_box.html", pot_candies=pot_candies)

@app.route("/normal")
def normal_candy():
    session["pot_candies"]-=10
    pot_candies=session["pot_candies"]
    return render_template("normal_candy.html", pot_candies=pot_candies)

@app.route("/cursed")
def cursed_candy():
    session["pot_candies"]=0
    return render_template("cursed_candy.html")

@app.route("/knock")
def knock():
    return render_template("knock.html")

@app.route("/knockstart")
def knock_start():
    session["gained_candies"]=0
    return render_template("knock_start.html")

@app.route("/midnightknock", methods=["POST","GET"])
def midnight_knock():
    if request.method=="POST":
        Type=random.choice(["normal","monster"])
        choice=request.form["choice"]
        if choice=="trick":
            if Type=="normal":
                return redirect("/tricknormal")
            elif Type=="monster":
                session["gained_candies"]+=30
                Database().add_candies(session["username"],30)
                return redirect("/trickmonster")
        elif choice=="treat":
            if Type=="normal":
                session["gained_candies"]+=30
                Database().add_candies(session["username"],30)
                return redirect("/treatnormal")
            elif Type=="monster":
                return redirect("/treatmonster")
    return render_template("midnight_knock.html")

@app.route("/treatnormal")
def treat_normal():
    candies=session["gained_candies"]
    return render_template("treat_normal.html",candies=candies)

@app.route("/treatmonster")
def treat_monster():
    candies=session["gained_candies"]
    session["gained_candies"]=0
    return render_template("treat_monster.html", candies=candies)

@app.route("/tricknormal")
def trick_normal():
    candies=session["gained_candies"]
    session["gained_candies"]=0
    return render_template("trick_normal.html", candies=candies)

@app.route("/trickmonster")
def trick_monster():
    candies=session["gained_candies"]
    return render_template("trick_monster.html", candies=candies)

@app.route("/detection")
def detection():
    return render_template("detection.html")

@app.route("/detectionstart")
def detection_start():
    monster=random.choice(Monsters)
    clues=Monster_clues[monster]
    first_clue=random.choice(clues)
    clues.remove(first_clue)
    session["clues"]=clues
    session["given_clues"]=[first_clue]
    session["monster"]=monster
    session["clues_used"]=0
    return redirect("/detectiongame")

@app.route("/addclues")
def add_clue():
    clues=session["clues"]
    next_clue=random.choice(clues)
    clues.remove(next_clue)
    session["clues"]=clues
    given_clues=session["given_clues"]
    given_clues.append(next_clue)
    session["given_clues"]=given_clues
    return redirect("/detectiongame")

@app.route("/detectiongame", methods=["POST","GET"])
def detection_game():
    if request.method=="POST":
        choice=request.form["choice"]
        if choice=="clue":
            if session["clues_used"]>=4:
                return render_template("detection_game.html", clues=session["given_clues"], clues_available=False)
            session["clues_used"]+=1
            return redirect("/addclues")
        elif choice==session["monster"].lower():
            return redirect("/monstermatch")
        else:
            session["guessed"]=choice
            return redirect("/monsterfail")
    return render_template("detection_game.html", clues=session["given_clues"], clues_available=True)

@app.route("/monstermatch")
def monster_match():
    monster=session["monster"]
    return render_template("monster_match.html", monster=monster)

@app.route("/monsterfail")
def monster_fail():
    monster=session["monster"]
    guessed=session["guessed"]
    return render_template("monster_fail.html", monster=monster, guessed=guessed)

@app.route("/gambleguide")
def gamble_guide():
    return render_template("gamble_guide.html")

@app.route("/knockguide")
def knock_guide():
    return render_template("/knock_guide.html")

@app.route("/deductionguide")
def deduction_guide():
    return render_template("deduction_guide.html")

@app.route("/guess")
def guess():
    return render_template("guess.html")

@app.route("/guessstart")
def guess_start():
    session["qna"]=[]
    return redirect("/guessgame")

@app.route("/guessgame", methods=["GET", "POST"])
def guess_game():
    choice=request.form.get("choice")
    if choice is not None:
        qna=session["qna"]
        qna.append([session["question"], choice])
        session["qna"]=qna
        print(session["qna"])
    response=Questions().model(session["qna"])
    print(response)
    if response[0].lower()=="yes":
        print("yes")
    session["question"]=response
    return render_template("guess_game.html",question=response)


app.run(debug=True)