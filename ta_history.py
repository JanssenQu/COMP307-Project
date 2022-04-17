from database import *
from orange_helpers import get_first_value


# checks if there is an user id associated with the name then runs a function to return data about the user
def get_user_data(func, fname, lname, base_case=[]):
    user_id = get_user_id_by_fname_lname(fname, lname)
    if user_id is None:
        return base_case
    result = func(user_id)
    return result


# for knowing when to display user not registered in website
def user_in_db(fname, lname):
    if get_user_id_by_fname_lname(fname, lname) is None:
        return False
    return True


def get_user_id_by_fname_lname(fname, lname):
    query_user_id = query_db(
        f"Select user_id FROM users WHERE first_name LIKE '{fname}' AND last_name LIKE '{lname}'")
    uid_list = list_query_items(query_user_id, "user_id")
    if len(uid_list) > 0:
        return uid_list[0]
    return None

# TA info/history
"""
    Table 1 TA personal info
    -TA_name as title
    legal_name, Student_ID, email, phone, location, degree, grad_ugrad, supervisor_name  
    
    
    Table 2 TA cohort
    term_month_year, courses_applied_for, priority(yes/no), hours(90/180), date_applied,  open_to_other_courses(yes/no), notes

    Table 3 Reviews
    -Average rating 
    -student rating comments 
    
    Table 4
    -professor performance log
    
    Table 5
    -prof wish list membership
    
    Table 6
    -the courses that are currently assigned to the TA this term

"""
def get_ta_personal_info(user_id):
    # user table: legal_name, email, phone, location,
    # student table: Student_ID, degree, grad_ugrad, supervisor_name
    # legal_name, Student_ID, email, phone, location, degree, grad_ugrad, supervisor_name

    data = []
    query_ta = query_db(f"Select * FROM users "
                        f"INNER JOIN students ON users.user_id = students.user_id "
                        f"WHERE users.user_id = {user_id}")
    for value in query_ta:
        legal_name = dict(value).get('legal_name')
        student_id = dict(value).get('student_id')
        email = dict(value).get('email')
        phone = dict(value).get('phone')
        location = dict(value).get('location')
        degree = dict(value).get('degree')
        grad_ugrad = dict(value).get('grad_ugrad')
        supervisor_name = dict(value).get('supervisor_name')
        data.append((legal_name, student_id, email, phone, location, degree, grad_ugrad, supervisor_name))

    return data


def get_application_details(user_id):
    data = []
    query_application = query_db(f"Select * FROM ta_cohort WHERE user_id = {user_id}")
    for value in query_application:
        cohort_id = dict(value).get('cohort_id')
        priority = dict(value).get('priority')
        hours = dict(value).get('hours')
        date_applied = dict(value).get('date_applied')
        open_to_other_courses = dict(value).get('open_to_other_courses')
        notes = dict(value).get('notes')

        courses_applied = ''
        query_course_application = query_db(f"Select * FROM ta_applied_courses WHERE cohort_id = {cohort_id}")
        for record in query_course_application:
            term = dict(record).get('course_term') # they all have the same term based on how ta cohort was imported
            courses_applied += f"{dict(record).get('course_term')}, "
        courses_applied = courses_applied[:-2] # take out the last ", "
        bool_dict = {1: "Yes", 0: "No"}
        data.append((term, courses_applied, bool_dict[priority], hours, date_applied, bool_dict[open_to_other_courses], notes))

    return data


# base_case = "NA"
def get_average_rating_of_ta(user_id):
    query_avg_rating = query_db(f"Select AVG(rating) FROM ta_reviews WHERE user_id = {user_id}")
    avg_rating = get_first_value(query_avg_rating, "AVG(rating)")
    if avg_rating is None:
        return "NA"
    return round(avg_rating,2)



def get_rating_comments_of_ta(user_id):
    data = []
    query_reviews = query_db(f"Select * FROM ta_reviews WHERE user_id = {user_id}")
    for value in query_reviews:
        rating = dict(value).get('rating')
        course_num = get_course_num(dict(value).get('course_id'))
        course_term = dict(value).get('course_term')
        review_desc = dict(value).get('review_desc')

        data.append((rating,course_num,course_term,review_desc))

    return data


def get_performance_log_of_ta(user_id):
    data = []
    query_performance_log = query_db(f"Select prof_id,course_id,course_term, comment "
                             f"FROM ta_performance_log WHERE ta_id = {user_id}")
    for value in query_performance_log:
        prof_name = get_name(dict(value).get('prof_id'))
        course_num = get_course_num(dict(value).get('course_id'))
        course_term = dict(value).get('course_term')
        comment = dict(value).get('comment')
        data.append((prof_name,course_num,course_term,comment))

    return data


def get_wishlist(user_id):
    data = []
    query_wishlist = query_db(f"Select prof_id,course_id,course_term FROM ta_wish_list WHERE ta_id = {user_id}")
    for value in query_wishlist:
        prof_name = get_name(dict(value).get('prof_id'))
        course_num = get_course_num(dict(value).get('course_id'))
        course_term = dict(value).get('course_term')
        data.append((prof_name,course_num,course_term))

    return data


def get_ta_courses(user_id):
    data = []
    query_ta_courses = query_db(f"Select * FROM ta_courses WHERE user_id = {user_id}")
    for value in query_ta_courses:
        course_num = get_course_num(dict(value).get('course_id'))
        course_term = dict(value).get('course_term')
        hours = dict(value).get('hours')
        data.append((course_num,course_term,hours))

    return data



# course TA history
"""
table of each TA with the courses they have been assigned to this term
courses they have been assigned to in the past

(a) select a TA to see all the courses they have been assigned to
(b) select a course number to see all the assigned TAs.

"""

# select a TA to see all the courses they have been assigned to
def get_courses_of_ta(fname, lname):
    user_id = get_user_id_by_fname_lname(fname, lname)
    if user_id is None:
        return []

    data = []
    query_ta_user_id = query_db(f"Select * FROM ta_courses WHERE user_id = {user_id}")
    for value in query_ta_user_id:
        course_num = get_course_num(dict(value).get('course_id'))
        course_term = dict(value).get('course_term')
        data.append((course_num,course_term))

    return data


def get_course_num(course_id):
    course_num = None
    query_course_num = query_db(f"Select course_num FROM courses WHERE course_id = {course_id}")
    for value in query_course_num:
        course_num = dict(value).get("course_num")
    return course_num


# select a course number to see all the assigned TAs
def get_tas_of_course(course_num,course_term):
    course_id = None
    query_course_id = query_db(
        f"Select course_id FROM courses WHERE course_num LIKE '{course_num}'")
    course_id_list = list_query_items(query_course_id, "course_id")
    if len(course_id_list) > 0:
        course_id = course_id_list[0]
    else:
        return ()

    data = []
    # gerate data for all terms
    if course_term == '':
        query_tas = query_db(f"Select user_id,course_term FROM ta_courses WHERE course_id = {course_id}")
        for value in query_tas:
            name = get_name(dict(value).get('user_id'))
            term = dict(value).get('course_term')
            data.append((name,term))
        return tuple(data)
    else:
        query_tas = query_db(f"Select user_id FROM ta_courses WHERE course_id = {course_id} AND course_term LIKE '{course_term}'")
        for value in query_tas:
            name = get_name(dict(value).get('user_id'))
            data.append((name,course_term))
        return tuple(data)


def get_name(user_id):
    query_course_num = query_db(f"Select first_name,last_name FROM users WHERE user_id = {user_id}")
    for value in query_course_num:
        fname = dict(value).get("first_name")
        lname = dict(value).get("last_name")
        return f"{fname} {lname}"
    return None