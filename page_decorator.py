from flask import redirect, render_template, request, url_for
from rate_ta_helper import *
from session import *
from user_registration_and_yellow_helpers import *

def page_decorator(page, post_func, session_id, *args):
    if session_id is None:
        return redirect(url_for("login"))
    new_session = verify_session(session_id)
    if new_session is None:
        return redirect(url_for("login"))
    elif new_session != session_id: # user has a session we update their session
        return redirect(url_for(page, session_id = new_session))
    post_result = post_func(session_id, *args)
    if post_result is None:
        return redirect(url_for("dashboard", session_id=session_id))
    return post_result


def dashboard_post(session_id):

    if request.method == 'POST':
        delete_session(session_id)
        return redirect(url_for("logout"))

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


def rate_ta_post(session_id, course_num, course_term):
    # select course
    course_list = get_courses_with_tas()
    if course_num is None and course_term is None:
        # if clicked on submit
        if request.method == 'POST':
            if request.form["choice"] == "choose_course":
                course_num = request.form.get('course')
                return redirect(url_for("rate_ta", session_id=session_id, course_num=course_num))
            # if it did not come from the right form
            return redirect(url_for("dashboard", session_id=session_id))
        # else just display select course
        return render_template('rate_ta_select_course.html', session_id=session_id, course_num=course_num,
                               course_list=course_list)

    # select term
    if course_num is not None and course_term is None:
        term_list = get_terms_with_tas(course_num)
        # if clicked on submit
        if request.method == 'POST':
            if request.form["choice"] == "choose_term":
                course_term = request.form.get('term')
                return redirect(url_for("rate_ta", session_id=session_id, course_num=course_num, course_term=course_term))
            # if it did not come from the right form
            return redirect(url_for("dashboard", session_id=session_id))
        # else just display select course
        return render_template('rate_ta_select_term.html', session_id=session_id, course_num=course_num,
                               term_list=term_list)

    # give rating
    if course_num is not None and course_term is not None:
        ta_names = get_tas(course_num, course_term)
        # if clicked on submit
        if request.method == 'POST':
            if request.form["choice"] == "rate_ta":
                ta = request.form['ta']
                stars = None
                try:
                    stars = request.form['rating']
                except:
                    return render_template('rate_ta.html', session_id=session_id, course_num=course_num,
                                           course_term=course_term, ta_names=ta_names, msg="Give a rating")
                comment = request.form['comment']
                insert_ta_rating(ta, course_num, course_term, stars, comment)
                return render_template('rate_ta.html', session_id=session_id, course_num=course_num,
                                       course_term=course_term, ta_names=ta_names, msg="Submitted")
            # if it did not come from the right form
            return redirect(url_for("dashboard", session_id=session_id))
        # else just display select course
        return render_template('rate_ta.html', session_id=session_id, course_num=course_num, course_term=course_term, ta_names=ta_names)


def ta_management_post(session_id, course_id):
    if has_access_to_blue(session_id):
        course_num_list = get_all_courses()
        if request.method == 'POST':
            course_num = request.form.get('course')
            course_id = get_course_id(course_num)
            return redirect(url_for("ta_management_dashboard", session_id=session_id, course_id=course_id, course_num=course_num))

        return render_template('ta_management.html', session_id=session_id,course_list=course_num_list)


def ta_admin_post(session_id):
    if has_access_to_orange(session_id):
        if request.method == 'POST':
            return render_template('ta_admin.html', session_id=session_id)

        return render_template('ta_admin.html', session_id=session_id)


def ta_management_dashboard_post(session_id, course_id, course_num):
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


def perf_log_post(session_id, course_id, course_num):
    if check_group(User.prof, session_id):
        course_term_list, ta_name_list = perf_log_dropdown_data(course_id)
        if request.method == 'POST':
            prof_id = get_user_id(session_id)
            course_term = request.form.get('term')
            ta_name = request.form.get('ta')
            comment = request.form["perf_log_notes"]
            ta_id = find_ta_id(ta_name, course_id, course_term)
            add_performance_log(prof_id, ta_id, course_id, course_term, comment)
            return render_template('perf_log.html', session_id=session_id, course_id=course_id, course_num=course_num, term_list=course_term_list, ta_list=ta_name_list,msg="Added")

        return render_template('perf_log.html', session_id=session_id, course_id=course_id, course_num=course_num, term_list=course_term_list, ta_list=ta_name_list)


def wishlist_post(session_id, course_id, course_num):
    if check_group(User.prof, session_id):
        term_list = next_two_semester()
        ta_list = get_ta_applications(course_id)  # todo
        if request.method == 'POST':
            prof_id = get_user_id(session_id)
            course_term = request.form.get('term')
            ta_name = request.form.get('ta')
            if ta_name is None:
                return render_template('wishlist.html', session_id=session_id, course_id=course_id,
                                        course_num=course_num, term_list=term_list, ta_list=ta_list,
                                        msg=f"No TA Available")

            ta_id = find_ta_id(ta_name, course_id, course_term)
            add_to_wishlist(course_id, course_term, prof_id, ta_id)
            return render_template('wishlist.html', session_id=session_id, course_id=course_id, course_num=course_num, term_list=term_list, ta_list=ta_list, msg=f"Added {ta_name}")

        return render_template('wishlist.html', session_id=session_id,course_id=course_id, course_num=course_num,term_list=term_list, ta_list=ta_list)


def sysop_tasks_post(session_id):
    if check_group(User.sys_op, session_id):
        return render_template('sysop_tasks.html', session_id=session_id)


def manage_users_post(session_id):
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


def manual_add_prof_course_post(session_id):
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


def import_prof_course_post(session_id):
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