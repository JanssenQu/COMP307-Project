from database import *
from session import *
from datetime import date


# returns the course id of the selected course in the dropdown in select course to be passed in the url
def get_course_id(course_num):
    query = query_db(f"Select course_id FROM courses WHERE course_num LIKE '{course_num}'")
    course_id = None
    for value in query:
        course_id = dict(value).get("course_id")
    return course_id


# below is for select course

# currently using get_all_courses() for select course
# we might use get_courses(session_id) instead if we want to use get_courses(session_id)
def get_all_courses():
    query = query_db(f"Select course_name, course_num FROM courses ")
    course_num_list = list_query_items(query, "course_num")
    return sorted(course_num_list)


# loads the term and TA dropdowns in performance log
def perf_log_dropdown_data(course_id):
    try:
        course_term_list = []
        ta_uid_list = []
        ta_name_list = []

        query_ta_courses = query_db(f"Select user_id,course_term FROM ta_courses WHERE course_id = {course_id}")
        for value in query_ta_courses:

            course_term = dict(value).get("course_term")
            if course_term not in course_term_list:
                course_term_list.append(course_term)

            user_id = dict(value).get("user_id")
            if user_id not in ta_uid_list:
                ta_uid_list.append(user_id)

        for user_id in ta_uid_list:
            query_ta_names = query_db(f"Select first_name,last_name FROM users WHERE user_id = {user_id}")
            for value in query_ta_names:
                ta_name_list.append(f'{dict(value).get("first_name")} {dict(value).get("last_name")}')

        return course_term_list, ta_name_list
    except sqlite3.OperationalError:
        return [],[]


# for submitting the ta perfomance log form
def add_performance_log(prof_id, ta_id, course_id, course_term, comment):
    mutate_db('INSERT INTO ta_performance_log VALUES (?,?,?,?,?,?)', [None, prof_id, ta_id, course_id, course_term, comment])
    return True


def find_ta_id(name, course_id, course_term):
    try:
        fname = name.split()[0]
        lname = name.split()[-1]

        query_user_id = query_db(f"Select user_id FROM users WHERE first_name LIKE '{fname}%' AND last_name LIKE '%{lname}'")
        uid_list = list_query_items(query_user_id, "user_id")

        ta_id = None
        for uid in uid_list:
            query = query_db(f"Select user_id FROM ta_courses WHERE user_id = {uid} AND course_id = {course_id} AND course_term = '{course_term}'")
            for value in query:
                ta_id = dict(value).get("user_id")

        return ta_id
    except:
        return None


# for the wishlist
def next_semester():
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    next_semester = ''

    if currentMonth >=2 and currentMonth <= 9:
        next_semester = f'Fall {currentYear}'
    else:
        next_semester = f'Winter {currentYear + 1}'

    return next_semester


# for the wishlist
def find_user_id_by_name(fname,lname):
    try:
        query_user_id = query_db(f"Select user_id FROM users WHERE first_name LIKE '{fname}%' AND last_name LIKE '%{lname}'")
        uid_list = list_query_items(query_user_id, "user_id")

        return uid_list[0]
    except:
        return None


# for submitting the wishlist form
def add_to_wishlist(course_id, term, prof_id, ta_id):
    if ta_id is None:
        return False

    mutate_db('INSERT INTO ta_wish_list VALUES (?,?,?,?,?)', [None, course_id, term, prof_id, ta_id])
    return True

