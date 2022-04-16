from database import *
import os
import csv
from encryption import *


# registration

def register_user(studentprof_id, fname, lname, email, usrname, pwd):
    # everyone is either a prof or a student
    # TA's can be profs or students
    # admins and sysops are profs

    # find user_id with the right name
    uid_list = []
    user_query = query_db(f"Select user_id FROM users WHERE first_name = '{fname}' AND last_name = '{lname}' AND username is NULL AND password IS NULL")
    for value in user_query:
        uid_list.append(dict(value).get('user_id'))

    student = False
    prof = False
    user_id = None
    for uid in uid_list:
        student_id_query = query_db(f"Select user_id FROM students WHERE user_id = {uid} AND student_id = {studentprof_id}")
        prof_id_query = query_db(f"Select user_id FROM profs WHERE user_id = {uid} AND prof_id = {studentprof_id}")
        for value in student_id_query:
            student = True
            user_id = dict(value).get('user_id')

        for value in prof_id_query:
            prof = True
            user_id = dict(value).get('user_id')

    # first check if they are TA, prof, admin, or sysop those users are already in the system we just want to update
    # the missing info such as the password or username
    # the user has to have the same name and student/prof id but no username and password

    # use update_user
    if user_id is not None:
        groups = {"tas":False,"admins":False,"sys_ops":False}
        for key in groups:
            group_query = query_db(f"Select user_id FROM {key} WHERE user_id = {user_id}")
            for value in group_query:
                groups[key] = True
        return update_user(user_id, studentprof_id, fname, lname, email, usrname, pwd, student, groups["tas"], prof, groups["admins"], groups["sys_ops"])

    # if not then just add regularly with add_user
    return add_user(studentprof_id, fname, lname, email, usrname, pwd, student=True, ta=False, prof=False, admin=False, sysop=False)



# Below is part of manage users
def find_users(name):
    fname, lname = name_splitter(name)
    user_list = []
    user_query = query_db(f"Select user_id,first_name,last_name,email,active FROM users "
                        f"WHERE first_name = '{fname}' OR last_name = '{lname}' OR last_name = '{fname}'"
                          f"OR username = '{name}'") # we might just get a last name
    for value in user_query:
        account_deactivated = "No"
        if dict(value).get("active") == 0:
            account_deactivated = "Yes"

        user_list.append( (dict(value).get("user_id"),dict(value).get("first_name"),dict(value).get("last_name"),dict(value).get("email"),account_deactivated))

    return tuple(user_list)


# add a new user
def add_user(studentprof_id, fname, lname, email, usrname, pwd, student, ta, prof, admin, sysop):
    has_email = query_db(f"SELECT email FROM users WHERE email='{email}'")
    has_user = query_db(f"SELECT username FROM users WHERE username='{usrname}'")

    if not has_email and not has_user:  # email and username has to be unique before adding
        # save to db
        if pwd is not None:
            hashed_pass = hash_password(pwd)
        else:
            hashed_pass = None
        mutate_db('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  [None, fname, lname, email, usrname, hashed_pass, None, None, None, True])

        # get the system user_id
        user_id = None
        for value in query_db(f"SELECT user_id FROM users WHERE email='{email}'"):
            user_id = dict(value).get('user_id')

        if student:
            mutate_db('INSERT INTO students VALUES (?, ?, ?, ?, ?)',
                      [user_id, studentprof_id, None, None, None])
        if ta:
            mutate_db('INSERT INTO tas VALUES (?)', [user_id])
        if prof:
            mutate_db('INSERT INTO profs VALUES (?, ?)', [user_id, studentprof_id])
        if admin:
            mutate_db('INSERT INTO admins VALUES (?)', [user_id])
        if sysop:
            mutate_db('INSERT INTO sys_ops VALUES (?)', [user_id])

        return True

    return False


# modify an existing user
def update_user(user_id, studentprof_id, fname, lname, email, usrname, pwd, student, ta, prof, admin, sysop):
    if user_id == '':
        return False

    try:
        user_id = int(user_id)

        others_email = query_db(f"SELECT email FROM users WHERE email='{email}' AND user_id != {user_id}")
        others_username = query_db(f"SELECT username FROM users WHERE username='{usrname}' AND user_id != {user_id}")

        if others_email or others_username:  # email and username has to be unique before adding
            return False

        if studentprof_id != '':
            studentprof_id = int(studentprof_id)

        # update the textbox values that have been filled
        if fname != '':
            mutate_db(f"UPDATE users SET first_name = '{fname}' WHERE user_id = {user_id}")
        if lname != '':
            mutate_db(f"UPDATE users SET last_name = '{lname}' WHERE user_id = {user_id}")
        if email != '':
            others_email = query_db(f"SELECT email FROM users WHERE email='{email}' AND user_id != {user_id}")
            if not others_email:
                mutate_db(f"UPDATE users SET email = '{email}' WHERE user_id = {user_id}")
        if usrname != '':
            others_username = query_db(f"SELECT username FROM users WHERE username='{usrname} AND user_id != {user_id}'")
            if not others_username:
                mutate_db(f"UPDATE users SET username = '{usrname}' WHERE user_id = {user_id}")
        if pwd != '':
            hashed_pass = hash_password(pwd)
            mutate_db(f"UPDATE users SET password = '{hashed_pass}' WHERE user_id = {user_id}")

        # update user group, delete from all
        tables = ["students","tas","profs","admins","sys_ops"]
        for table in tables:
            mutate_db(f'DELETE FROM {table} WHERE user_id = {user_id}')
        # update user group, add new
        if student:
            mutate_db('INSERT INTO students VALUES (?, ?, ?, ?, ?)',
                      [user_id, studentprof_id, None, None, None])
        if ta:
            mutate_db('INSERT INTO tas VALUES (?)', [user_id])
        if prof:
            mutate_db('INSERT INTO profs VALUES (?, ?)', [user_id, studentprof_id])
        if admin:
            mutate_db('INSERT INTO admins VALUES (?)', [user_id])
        if sysop:
            mutate_db('INSERT INTO sys_ops VALUES (?)', [user_id])

        return True

    except ValueError:
        return False


def delete_user(user_id):
    try:
        tables = ["users", "admins", "sys_ops", "students", "tas", "profs", "teaching_courses", "ta_courses", "registered_courses","sessions"]
        for table in tables:
            mutate_db(f"DELETE FROM {table} WHERE user_id = '{int(user_id)}';")
        return True
    except ValueError:
        return False


# disallow login to user
def deactivate_user(user_id):
    try:
        mutate_db(f"UPDATE users SET active = 0 WHERE user_id = {int(user_id)};")
    finally:
        return


def reactivate_user(user_id):
    try:
        mutate_db(f"UPDATE users SET active = 1 WHERE user_id = {int(user_id)};")
    finally:
        return


# Below is part of manual and csv import of prof course

def add_prof_course_cvs_to_db(filepath):
    lines_failed_to_add = []
    with open(filepath) as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            # check if in the db
            if len(row) == 4:  # check formatting
                term_month_year, course_num, course_name, instructor_assigned_name = row[0], row[1], row[2], \
                                                                                     row[3]
                if term_month_year == 'term_month_year' and course_num == 'course_num' and course_name == 'course_name' and instructor_assigned_name == 'instructor_assigned_name':
                    continue

                added = add_prof_course_to_db(term_month_year, course_num, course_name, instructor_assigned_name)
                if not added:
                    lines_failed_to_add.append(row)
            else:
                lines_failed_to_add.append(row)

    os.remove(filepath)

    return lines_failed_to_add



def name_splitter(instructor_assigned_name):
    """
    Separates a full name into first and last name
    the first name would be the first word only
    last name would be everything else after the first word
    :param instructor_assigned_name: full name of a person
    :return: tuple fname, lname
    """
    try:
        first, *last = instructor_assigned_name.split()
        fname = first
        lname = " ".join(last)
        return fname, lname
    except ValueError:
        return '',''


def add_prof_course_to_db(term_month_year, course_num, course_name, instructor_assigned_name):
    '''
    used for manual and csv import of prof courses

    if the instructor is registered in the db
    Add the instructor, course and term to the teaching_courses table
    and if the course or term is not in the db then it will add them to their corresponding tables

    :param term_month_year: string of term and year
    :param course_num: string for the course number
    :param course_name: string for the course name
    :param instructor_assigned_name: full name of the instructor
    :return: True if added else False
    '''

    # is the instructor is registered and get the id
    fname, lname = name_splitter(instructor_assigned_name)
    user_ids = query_db(f"Select user_id FROM users "
                        f"WHERE first_name = '{fname}' AND last_name = '{lname}'")
    user_id = None
    for value in user_ids:
        user_id = dict(value).get("user_id")

    # add the data
    if user_id is not None:
        # is the course offered and get the id
        course_ids = query_db(f"Select course_id FROM courses "
                              f"WHERE course_name = '{course_name}' AND course_num = '{course_num}'")
        course_id = None
        for value in course_ids:
            course_id = dict(value).get("course_id")

        # is the course offered during that term
        has_term = query_db(f"Select course_term FROM course_terms "
                            f"WHERE course_id = '{course_name}' AND course_term = '{term_month_year}'")

        """
        4 cases
        1. all there
        2. course and term already there so we just add to teaching_courses
        3. only course there so we add term then teaching_courses
        4. course not there so we add course then term then teaching_courses
        """
        prof_courses = query_db(f"Select user_id FROM teaching_courses "
                            f"WHERE user_id = {user_id} AND course_id = '{course_id}' AND course_term = '{term_month_year}'")
        already_teaching = None
        for value in prof_courses:
            already_teaching = dict(value).get("user_id")

        if already_teaching is not None:
            return True

        # case 2
        if course_id is not None and has_term:
            mutate_db('INSERT INTO teaching_courses VALUES (?,?,?)', [user_id, course_id, term_month_year])
            return True

        # case 3
        if course_id is not None:
            mutate_db('INSERT INTO course_terms VALUES (?,?)', [course_id, term_month_year])
            mutate_db('INSERT INTO teaching_courses VALUES (?,?,?)', [user_id, course_id, term_month_year])
            return True

        # case 4
        mutate_db('INSERT INTO courses VALUES (?,?,?,?)', [None, course_name, course_num, 'na'])
        course_ids = query_db(f"Select course_id FROM courses "
                              f"WHERE course_name = '{course_name}' AND course_num = '{course_num}'")
        for value in course_ids:
            course_id = dict(value).get("course_id")
        mutate_db('INSERT INTO course_terms VALUES (?,?)', [course_id, term_month_year])
        mutate_db('INSERT INTO teaching_courses VALUES (?,?,?)', [user_id, course_id, term_month_year])
        return True

    return False

