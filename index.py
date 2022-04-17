from flask import Flask, redirect, url_for, render_template, request
from database import *
from encryption import *
from page_decorator import *
from session import *
from user_registration_and_yellow_helpers import *
from rate_ta_helper import *
from blue_helpers import *


app = Flask(__name__)


# GREEN
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login/", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        usr = request.form['usrname']
        pwd = request.form['psw']
        user = verify_user(usr, pwd)
        if user:
            session_key = create_session(user['user_id'])
            return redirect(url_for("dashboard", session_id=session_key))
        else:
            msg = 'Wrong username or password.'
            return render_template('login.html', msg=msg)

    return render_template("login.html")

@app.route("/logout/")
def logout():
    return render_template('logout.html')


@app.route("/register/", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # get form items
        studentprof_id = request.form['uid']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        usrname = request.form['usrname']
        pwd = request.form['psw']

        if register_user(studentprof_id, fname, lname, email, usrname, pwd):
            return redirect(url_for("login"))
        else:
            msg = 'The student ID, username or email has already been registered.' \
                  'Please retry.'
            return render_template('register.html', msg=msg)

    return render_template('register.html')


@app.route("/dashboard/")
@app.route("/dashboard/<session_id>", methods=['GET', 'POST'])
def dashboard(session_id=None):
    return page_decorator("dashboard", dashboard_post, session_id)


@app.route("/rate_ta/")
@app.route("/rate_ta/<session_id>", methods=['GET', 'POST'])
@app.route("/rate_ta/<session_id>/<course_num>", methods=['GET', 'POST'])
@app.route("/rate_ta/<session_id>/<course_num>/<course_term>", methods=['GET', 'POST'])
def rate_ta(session_id=None, course_num=None, course_term=None):
    return page_decorator("rate_ta", rate_ta_post, session_id, course_num, course_term)

# ORANGE
@app.route("/ta_admin/")
@app.route("/ta_admin/<session_id>", methods=['GET', 'POST'])
def ta_admin(session_id=None):
    return page_decorator("ta_admin", ta_admin_post, session_id)


@app.route("/ta_info_history/")
@app.route("/ta_info_history/<session_id>", methods=['GET', 'POST'])
def ta_info_history(session_id=None):
    return page_decorator("ta_info_history", ta_info_history_post, session_id)


@app.route("/course_ta_history/")
@app.route("/course_ta_history/<session_id>", methods=['GET', 'POST'])
def course_ta_history(session_id=None):
    return page_decorator("course_ta_history", course_ta_history_post, session_id)


@app.route("/add_ta/")
@app.route("/add_ta/<session_id>", methods=['GET', 'POST'])
def add_ta(session_id=None):
    return page_decorator("add_ta", add_ta_post, session_id)


@app.route("/remove_ta/")
@app.route("/remove_ta/<session_id>", methods=['GET', 'POST'])
def remove_ta(session_id=None):
    return page_decorator("remove_ta", remove_ta_post, session_id)


# BLUE
@app.route("/ta_management/")
@app.route("/ta_management/<session_id>", methods=['GET', 'POST'])
def ta_management(session_id=None, course_id=None):
    return page_decorator("ta_management", ta_management_post, session_id, course_id)


@app.route("/ta_management_dashboard/")
@app.route("/ta_management_dashboard/<session_id>")
@app.route("/ta_management_dashboard/<session_id>/<course_id>/<course_num>", methods=['GET', 'POST'])
def ta_management_dashboard(session_id=None, course_id=None, course_num=None):
    return page_decorator("ta_management_dashboard", ta_management_dashboard_post, session_id, course_id, course_num)


@app.route("/perf_log/")
@app.route("/perf_log/<session_id>")
@app.route("/perf_log/<session_id>/<course_id>/<course_num>", methods=['GET', 'POST'])
def perf_log(session_id=None, course_id=None, course_num=None):
    return page_decorator("perf_log", perf_log_post, session_id, course_id, course_num)


@app.route("/wishlist/")
@app.route("/wishlist/<session_id>")
@app.route("/wishlist/<session_id>/<course_id>/<course_num>", methods=['GET', 'POST'])
def wishlist(session_id=None, course_id=None, course_num=None):
    return page_decorator("wishlist", wishlist_post, session_id, course_id, course_num)


# YELLOW
@app.route("/sysop_tasks/")
@app.route("/sysop_tasks/<session_id>")
def sysop_tasks(session_id=None):
    return page_decorator("sysop_tasks", sysop_tasks_post, session_id)


# manage users and find
@app.route("/manage_users/")
@app.route("/manage_users/<session_id>", methods=['GET', 'POST'])
def manage_users(session_id=None):
    return page_decorator("manage_users", manage_users_post, session_id)


@app.route("/manual_add_prof_course/")
@app.route("/manual_add_prof_course/<session_id>", methods=['GET', 'POST'])
def manual_add_prof_course(session_id=None):
    return page_decorator("manual_add_prof_course", manual_add_prof_course_post, session_id)


@app.route("/import_prof_course/")
@app.route("/import_prof_course/<session_id>", methods=['GET', 'POST'])
def import_prof_course(session_id=None):
    return page_decorator("import_prof_course", import_prof_course_post, session_id)


if __name__ == "__main__":
    app.run()