from flask import Flask, redirect, url_for, render_template, request
from database import *
from encryption import *
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
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id: # user has a session we update their session
        return redirect(url_for("dashboard", session_id = new_session))

    if request.method == 'POST':
        delete_session(session_id)
        return redirect(url_for("logout"))

    # use the session id to gather all information about the user to display it on dashboard
    ta_admin =''
    if has_access_to_orange(session_id):
        ta_admin = "TA Admin"

    ta_management =''
    if has_access_to_blue(session_id):
        ta_management = "TA Management"

    sysop_tasks =''
    if check_group(User.sys_op, session_id):
        sysop_tasks = "Sysop Tasks"

    return render_template('dashboard.html', session_id=session_id, ta_admin=ta_admin, ta_management=ta_management, sysop_tasks=sysop_tasks)


@app.route("/rate_ta/")
@app.route("/rate_ta/<session_id>", methods=['GET', 'POST'])
def rate_ta(session_id=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:
        return redirect(url_for("rate_ta", session_id = new_session))

    script = rate_ta_dependent_dropdown_script()

    if request.method == 'POST':
        course_num = request.form['course']
        term = request.form['term']
        ta = request.form['ta']
        stars = request.form['rating']
        comment = request.form['comment']

        try:
            insert_ta_rating(ta, course_num, term, stars, comment)
        finally:
            return render_template('rate_ta.html', session_id=session_id, script=script)

    # use the session id to gather all information about the user to display it on dashboard
    return render_template('rate_ta.html', session_id=session_id, script=script)

# ORANGE
@app.route("/ta_admin/")
@app.route("/ta_admin/<session_id>")
def ta_admin(session_id=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id: # user's session will be updated
        if has_access_to_orange(session_id):
            return redirect(url_for("ta_admin", session_id=new_session))
        return redirect(url_for("dashboard", session_id=new_session))
    if has_access_to_orange(session_id):
        if request.method == 'POST':
            return render_template('ta_admin.html', session_id=session_id)

        return render_template('ta_admin.html', session_id=session_id)
    return redirect(url_for("dashboard", session_id=session_id))

# BLUE
@app.route("/ta_management/")
@app.route("/ta_management/<session_id>", methods=['GET', 'POST'])
def ta_management(session_id=None, course_id=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:  # user's session will be updated
        if has_access_to_blue(session_id):
            return redirect(url_for("ta_management", session_id=new_session))
        return redirect(url_for("dashboard", session_id=new_session))
    if has_access_to_blue(session_id):
        course_num_list = get_all_courses()
        if request.method == 'POST':
            course_num = request.form.get('course')
            course_id = get_course_id(course_num)
            return redirect(url_for("ta_management_dashboard", session_id=new_session, course_id=course_id, course_num=course_num))

        return render_template('ta_management.html', session_id=session_id,course_list=course_num_list)
    return redirect(url_for("dashboard", session_id=session_id))


@app.route("/ta_management_dashboard/")
@app.route("/ta_management_dashboard/<session_id>")
@app.route("/ta_management_dashboard/<session_id>/<course_id>/<course_num>", methods=['GET', 'POST'])
def ta_management_dashboard(session_id=None, course_id=None, course_num=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:  # user's session will be updated
        if has_access_to_blue(session_id):
            return redirect(url_for("ta_management", session_id=new_session))
        return redirect(url_for("dashboard", session_id=new_session))
    if has_access_to_blue(session_id):
        # use the session id to gather all information about the user to display it on dashboard
        perf_log = ''
        if check_group(User.prof, session_id):
            perf_log = "TA Performance Log"

        wish_list = ''
        if check_group(User.prof, session_id):
            wish_list = "TA Wish List"

        if request.method == 'POST':
            return render_template('ta_management_dashboard.html', session_id=session_id,course_id=course_id, course_num=course_num, perf_log=perf_log, wish_list=wish_list)

        return render_template('ta_management_dashboard.html', session_id=session_id,course_id=course_id, course_num=course_num, perf_log=perf_log, wish_list=wish_list)

    return redirect(url_for("dashboard", session_id=session_id))


@app.route("/perf_log/")
@app.route("/perf_log/<session_id>")
@app.route("/perf_log/<session_id>/<course_id>/<course_num>", methods=['GET', 'POST'])
def perf_log(session_id=None, course_id=None, course_num=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:  # user's session will be updated
        if check_group(User.prof, session_id):
            return redirect(url_for("ta_management", session_id=new_session))
        return redirect(url_for("dashboard", session_id=new_session))
    if check_group(User.prof, session_id):
        return render_template('perf_log.html', session_id=session_id, course_id=course_id, course_num=course_num)
    return redirect(url_for("dashboard", session_id=session_id))


@app.route("/wishlist/")
@app.route("/wishlist/<session_id>")
@app.route("/wishlist/<session_id>/<course_id>/<course_num>", methods=['GET', 'POST'])
def wishlist(session_id=None, course_id=None, course_num=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:  # user's expired session will be updated
        if check_group(User.prof, session_id):
            return redirect(url_for("ta_management", session_id=new_session))
        return redirect(url_for("dashboard", session_id=new_session))
    if check_group(User.prof, session_id):
        return render_template('wishlist.html', session_id=session_id,course_id=course_id, course_num=course_num)

    return redirect(url_for("dashboard", session_id=session_id))



# YELLOW
@app.route("/sysop_tasks/")
@app.route("/sysop_tasks/<session_id>")
def sysop_tasks(session_id=None):
    ### v Access check v ###
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id: # user's session will be updated
        if check_group(User.sys_op, session_id):
            return redirect(url_for("sysop_tasks", session_id=new_session))
        return redirect(url_for("dashboard", session_id=new_session))
    if check_group(User.sys_op, session_id):
        return render_template('sysop_tasks.html', session_id=session_id)
    ### ^ Access check ^ ###

    return redirect(url_for("dashboard", session_id=session_id))


# manage users and find
@app.route("/manage_users/")
@app.route("/manage_users/<session_id>", methods=['GET', 'POST'])
def manage_users(session_id=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:
        return redirect(url_for("manage_users", session_id=new_session))

    if check_group(User.sys_op, session_id):
        if request.method == 'POST':
            # check which submit button was used
            # find user
            if request.form["choice"] == "find":
                search = request.form['search']
                if search != "":
                    if "search" in request.form:
                        name = request.form['search']
                        headings = ("System User ID", "First Name", "Last Name", "Email", "Account Deactivated")
                        data = find_users(name)
                        if len(data) > 0:
                            return render_template('manage_users.html', headings=headings, data=data, session_id=session_id)
                        return render_template('manage_users.html', headings=headings, session_id=session_id)
                return render_template('manage_users.html', session_id=session_id)

            # add user
            if request.form["choice"] == "add":
                # get form items
                studentprof_id = int(request.form['uid'])
                fname = request.form['fname']
                lname = request.form['lname']
                email = request.form['email']
                usrname = None
                pwd = None
                # checkboxes
                student = request.form.getlist('student')  # empty list if not checked "Student" if checked
                ta = request.form.getlist('ta')
                prof = request.form.getlist('prof')
                admin = request.form.getlist('admin')
                sysop = request.form.getlist('sysop')

                if add_user(studentprof_id, fname, lname, email, usrname, pwd, student, ta, prof, admin, sysop):
                    return render_template('manage_users.html', session_id=session_id,msg="added")
                else:
                    msg = 'The student ID, username or email has already been registered.' \
                          'Please retry.'
                    return render_template('manage_users.html', session_id=session_id,msg=msg)

            # edit user
            if request.form["choice"] == "edit":
                # get form items
                system_user_id = request.form['system_uid']
                studentprof_id = request.form['uid_update']
                fname = request.form['fname_update']
                lname = request.form['lname_update']
                email = request.form['email_update']
                usrname = request.form['usrname_update']
                pwd = request.form['psw_update']
                # checkboxes
                student = request.form.getlist('student_update')  # empty list if not checked "Student" if checked
                ta = request.form.getlist('ta_update')
                prof = request.form.getlist('prof_update')
                admin = request.form.getlist('admin_update')
                sysop = request.form.getlist('sysop_update')

                if update_user(system_user_id, studentprof_id, fname, lname, email, usrname, pwd, student, ta, prof, admin, sysop):
                    return render_template('manage_users.html', session_id=session_id,msg="updated")
                return render_template('manage_users.html', session_id=session_id, msg="failed to update")

            # delete
            if request.form["choice"] == "delete":
                user_id = request.form["usrdelete"]
                if delete_user(user_id):
                    return render_template('manage_users.html', session_id=session_id, msg=f"deleted {user_id}")
                return render_template('manage_users.html', session_id=session_id, msg="failed to delete")

            # deactivate
            if request.form["choice"] == "deactivate":
                deactivate_user(request.form["usrdeactivate"])
                return render_template('manage_users.html', session_id=session_id)

            # reactivate
            if request.form["choice"] == "reactivate":
                reactivate_user(request.form["usrreactivate"])
                return render_template('manage_users.html', session_id=session_id)

        return render_template('manage_users.html', session_id=session_id)

    return redirect(url_for("dashboard", session_id=session_id))



@app.route("/manual_add_prof_course/")
@app.route("/manual_add_prof_course/<session_id>", methods=['GET', 'POST'])
def manual_add_prof_course(session_id=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:
        return redirect(url_for("manual_add_prof_course", session_id=new_session))

    if check_group(User.sys_op, session_id):
        msg = ''
        if request.method == 'POST':
            # get form items
            term = request.form['term_month_year']
            course_num = request.form['course_num']
            course_name = request.form['course_name']
            instructor = request.form['instructor_assigned_name']

            added = add_prof_course_to_db(term, course_num, course_name, instructor)

            if added:
                msg = 'Added'
                return render_template('manual_add_prof_course.html', msg=msg, session_id=session_id)

            else:
                msg = 'Failed to add, instructor not registered'
                return render_template('manual_add_prof_course.html', msg=msg, session_id=session_id)

        return render_template('manual_add_prof_course.html',session_id=session_id)
    return redirect(url_for("dashboard", session_id=session_id))


@app.route("/import_prof_course/")
@app.route("/import_prof_course/<session_id>", methods=['GET', 'POST'])
def import_prof_course(session_id=None):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id:
        return redirect(url_for("import_prof_course", session_id=new_session))

    if check_group(User.sys_op, session_id):
        #assumes that prof is already in the users table of the database
        msg = ''
        data = []
        if request.method == 'POST':
            if request.files:
                uploaded_file = request.files['file']
                if str.lower(uploaded_file.filename[-4:]) != ".csv":
                    msg = 'Please upload a csv file'
                    return render_template('import_prof_course.html', msg=msg, session_id=session_id)

                filepath = os.path.join('dir_for_csv', uploaded_file.filename)
                uploaded_file.save(filepath)
                lines_failed_to_add = add_prof_course_cvs_to_db(filepath)
                msg = 'Data added'
                if len(lines_failed_to_add) > 0:
                    msg = f'Failed to add the following rows {lines_failed_to_add}. Please verify that the instructor is ' \
                          f'registered and the file is correctly formatted as term_month_year, course_num, course_name, ' \
                          f'instructor_assigned_name'

                return render_template('import_prof_course.html', msg=msg, session_id=session_id)

        return render_template('import_prof_course.html', session_id=session_id)
    return redirect(url_for("dashboard", session_id=session_id))




if __name__ == "__main__":
    app.run()