from flask import Blueprint, render_template, redirect, url_for, request

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET','POST'])
def login():
    return render_template("login.html")

@auth.route("/sign-up", methods=['GET','POST'])
def sign_up():
    data = request.form.get()
    return render_template("register.html")

@auth.route("/logout", methods=['GET','POST'])
def sign_up():
    return redirect(url_for("views.home"))

