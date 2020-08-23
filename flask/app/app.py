import json


from flask import Flask, flash, redirect, render_template, request, session, url_for
from mongoengine import *
import re


##=============================================##
##======== IMPORTING SEPARATE CLASSES =========##
##=============================================##
from movies import Movies
from users import Users
from screenings import Screenings
from editScr import EditScr

##=============================================##
##====== CONNECTIONS & APP CONFIGURATION ======##
##=============================================##


# app initialization
app = Flask(__name__)

# MongoEngine db init connection. By default:localhost
connect("InfoCinemas",host="172.18.0.2",port=27017)

# Secret key for session cookie
app.secret_key = "infoCinemas1234"
app.config["SECRET_KEY"] = "TopSecretNobodyKnows"

##=============================================##
##=================== ROUTES ==================##
##=============================================##


##===========================##
##======= USER ACTIONS ======##
##===========================##

# LandingPage of the site. If not logged in, it displays the login form and the signup link.
# If logged in, displays the user or admin panel accordingly.
@app.route("/", methods=["GET", "POST"])
def index():
    if "email" in session:
        if session["category"] == "user":
            print("A user logged in")
            return render_template("userpanel.html")
        else:
            print("An admin logged in")
            return render_template("adminpanel.html")

    return render_template("index.html")


# Route for handling login page.
# Takes username input from form and checks if it exists.
# If yes, then proceeds to check if the given password is correct.
# If both correct, redirects user to index.html
# If either one is false, returns error message
@app.route("/login", methods=["POST"])
def login():
    try:
        login_user = Users.objects(email=request.form["email"]).get()
        if login_user:
            if login_user.password == request.form["pass"]:
                session["email"] = request.form["email"]
                session["category"] = login_user.category
                print("session cookie category is:" + login_user.category)
                return redirect(url_for("index"))
            else:
                return "Invalid username/password combination"
    except DoesNotExist:
        return "Invalid username/password combination"


# Route for handling login page.
# Takes user data from form.
# If username exists on db, returns error message.
# If not, creates the user on the db with the following data (username,email,hashed given password)
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            existing_user = Users.objects(email=request.form["email"]).get()
            if existing_user:
                return "User already exists!"
        except DoesNotExist:
            new_user_data = Users(
                name=request.form["username"],
                email=request.form["email"],
                password=request.form["pass"],
                category="user",
            ).save()
            session["email"] = request.form["email"]
            session["category"] = "user"
            return redirect(url_for("index"))

    return render_template("register.html")


# Route to handle logout
# Cleans the session cookie
@app.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("category", None)
    flash("You logged out!")
    return redirect(url_for("index"))


# Route for the user to delete his account himself
# Removes user credentials from database
@app.route("/deleteYourAccount", methods=["GET"])
def deleteAccount():
    usertoDelete = session["email"]
    if usertoDelete:
        Users.objects(email=usertoDelete).delete()
        session.pop("email", None)
        session.pop("category", None)
        return "System user Account Deleted - KABOOM"


# Route to handle the "search for a movie" functionality.
# Search is only done by title. Displays Search results below the form
@app.route("/searchmovie", methods=["POST", "GET"])
def searchmovie():

    q_title = request.form.get("title")
    res = []
    if q_title:
        try:
            res = Movies.objects(title__contains=q_title)
        except DoesNotExist:
            flash("No such movie", category="error")

    return render_template("finder.html", results=res)


# Displays the movie details
@app.route("/show/<string:id>", methods=["GET", "POST"])
def show(id):
    try:
        res = Movies.objects(id=id).get()

    except DoesNotExist:
        return "No movie found! Problem with id."

    return render_template("showmovie.html", result=res)


# Displays the available screenings, given a valid movie id.
@app.route("/viewscreenings/<string:id>", methods=["GET", "POST"])
def viewScr(id):
    try:
        screenings = Screenings.objects(movieId=id)

    except DoesNotExist:
        return "No movie found to buy tickets for. Bad movie id"

    return render_template("viewscr.html", screenings=screenings)


# Displays the viewing history. A list with all the movie titles a user has purchased a ticket to.
@app.route("/history", methods=["POST", "GET"])
def history():
    user = Users.objects(email=session["email"]).get()
    viewHistory = user.moviesSeen
    viewHistory_titles = user.mSeenTitles

    return render_template("history.html", history=viewHistory_titles)


# Handles the purchase of tickets.
# Given a valid screening id, a query for the number of available seats is made to the db.
# From there, displays a page with a select html field with only these many options for number of tickets available to buy.
# If availability is zero, it displays zero.
# After user has purchased a number of tickets, the screening availability is decreased accordingly and a corresponding message is displayed.
# Also, the screening id and the movie title are saved to the user.object on the database on separate "parallel" lists.
@app.route("/purchase/<string:id>", methods=["GET", "POST"])
def purchase(id):

    scrtoBuy = Screenings.objects(id=id).get()
    avail = scrtoBuy.available
    if request.method == "POST":
        requested = request.form["num"]
        remain = avail - int(request.form["num"])
        if remain > 0:
            try:
                scrtoBuy.update(available=remain)
                updUH = Users.objects(email=session["email"]).get()

                mSeen = scrtoBuy.movieId.to_dbref()
                mTitle = scrtoBuy.movieTitle

                updUH.update(push__moviesSeen=mSeen)
                updUH.update(push__mSeenTitles=mTitle)
                updUH.save()
            except ValidationError:
                return "Not enough tickets available!"

        flash("You have reserved " + request.form["num"] + " ticket(s)!")
        redirect(url_for("index"))

    return render_template("purchase.html", avail=avail)


##===========================##
##====== ADMIN ACTIONS ======##
##===========================##

# Displays the administrator panel
@app.route("/adminpanel", methods=["POST", "GET"])
def adminpanel():
    render_template("adminpanel.html")
    return "Nothing yet"


# Allows the addition of a new movie to the database
@app.route("/moviemanagement", methods=["POST", "GET"])
def moviemanagement():
    if request.method == "POST":
        in_title = request.form["title"]
        in_year = request.form["year"]
        in_description = request.form["description"]
        new_movie = Movies(title=in_title, year=in_year, description=in_description)

        try:
            new_movie.save()
            print("success insert")
        except:
            print("There was an error inserting a movie")

    all_movies = Movies.objects()
    return render_template("moviemanagement.html", movies=all_movies)


# Allows the edit of the movie details and registers the new information to the database
@app.route("/updatemovie/<string:id>", methods=["POST", "GET"])
def updatemovie(id):
    mScreenings = Screenings.objects(movieId=id)
    movie = Movies.objects(id=id).get()
    if request.method == "POST":
        new_title = request.form["title"]
        new_year = request.form["year"]
        new_descr = request.form["description"]

        try:
            movie.update(title=new_title, year=new_year, description=new_descr)
            return redirect(request.referrer)
        except DoesNotExist:
            return "Error updating movie details"

    return render_template(
        "updatemovie.html", allScreenings=mScreenings, selMovie=movie
    )


# Removes a movie from the database
@app.route("/deletemovie/<string:id>", methods=["POST", "GET"])
def deletemovie(id):
    movietoDelete = Movies.objects(id=id).get()
    if movietoDelete:
        movietoDelete.delete()
        print("Deleted movie " + movietoDelete.title + " from system")
    return redirect("/moviemanagement")


# Route to edit the screenings of a movie. Allow the addition and deletion
# of the screenings given a movie id
@app.route("/editscreenings/<string:id>", methods=["POST", "GET"])
def editscr(id):
    availScr = Screenings.objects(movieId=id)
    m_obj = Movies.objects(id=id).get()
    mTitle = m_obj.title
    scrForm = EditScr()
    if scrForm.validate_on_submit():
        newTD = "{}-{}-{} {}:{}".format(
            scrForm.scrDay.data,
            scrForm.scrMonth.data,
            scrForm.scrYear.data,
            scrForm.scrHours.data,
            scrForm.scrMinutes.data,
        )
        try:
            newScr = Screenings(
                movieId=id, scrTime=newTD, available=50, movieTitle=mTitle
            )
            newScr.save()
        except DoesNotExist:
            return "Error adding new screening"

    return render_template("editscreenings.html", form=scrForm, screenings=availScr)


# Route to delete registered screening of a movie given a valid screening id.
@app.route("/deleteScreening/<string:id>", methods=["POST", "GET"])
def deleteScreening(id):
    scrToDelete = Screenings.objects(id=id).get()
    if scrToDelete:
        try:
            scrToDelete.delete()
            print("Deleted screening " + scrToDelete.scrTime + " from db")
        except DoesNotExist:
            return "Error deleting screening"

    return redirect(request.referrer)


# When called, if the session coockie is of a user, redirects to index, which redirects to User Panel
# if the session cookie is of an admin then renders the user management page with all the system "normal" users.
# From there, an admin may change a users's status or delete a normal user account.
# Admin, cannot delete Admins
@app.route("/usermanagement", methods=["POST", "GET"])
def usermanagement():
    if session["category"] == "user":
        return redirect("/")
    else:
        all_users = Users.objects()
        if request.method == "POST":
            try:
                existing_user = Users.objects(email=request.form["email"]).get()
                if existing_user:
                    return "An admin with this email already exists!"
            except DoesNotExist:
                new_admin_data = Users(
                    name=request.form["username"],
                    email=request.form["email"],
                    password=request.form["pass"],
                    category="admin",
                ).save()
                return redirect(url_for("usermanagement"))

    return render_template("usermanagement.html", users=all_users)


# Takes a user id and passes it to a query executed on the Users collection.
# If the id is found the object's value of "category" attribute is changed to admin
# and then redirects to index, which redirects to Admin Panel.
@app.route("/change/<string:id>", methods=["POST", "GET"])
def change(id):
    usertoChange = Users.objects(id=id).get()
    if usertoChange:
        if usertoChange.category == "user":
            usertoChange.category = "admin"
            usertoChange.save()
            print("Changed user " + usertoChange.name + " to admin")
        else:
            return "User was already an Admin"

    return redirect("/usermanagement")


# Takes a user id and passes it to a query executed on the Users collection.
# If the id is found the object is deleted and then redirects to index,
# which redirects to Admin Panel
@app.route("/deleteUser/<string:id>", methods=["POST", "GET"])
def deleteUser(id):
    usertoDelete = Users.objects(id=id).get()
    if usertoDelete:
        usertoDelete.delete()
        print("Deleted user " + usertoDelete.name + " from system")

    return redirect("/usermanagement")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

