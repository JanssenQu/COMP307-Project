from database import *
from blue_helpers import *
from user_registration_and_yellow_helpers import *

def find_user_id_by_name_and_school_id(fname, lname, school_id):
    # find potential user_id based on first name last name
    query_user_id = query_db(
        f"Select user_id FROM users WHERE first_name LIKE '%{fname}%' AND last_name LIKE '%{lname}%'")
    uid_list = list_query_items(query_user_id, "user_id")

    # find the user that has the same student/prof id and return that user_id
    for uid in uid_list:
        query_prof_id = query_db(f"SELECT user_id FROM profs WHERE prof_id = {school_id} AND user_id = {uid}")
        query_student_id = query_db(f"SELECT user_id FROM students WHERE student_id = {school_id} AND user_id = {uid}")

        prof_id_list = list_query_items(query_prof_id, "user_id")
        student_id_list = list_query_items(query_student_id, "user_id")

        for uid in prof_id_list:
            return uid

        for uid in student_id_list:
            return uid

    return None


def add_ta(fname, lname, student_id, course_num, course_term, hours, email, group):
    '''
    SQL Add TA to Course in the orange area TA administration
    Tables affected
    tas
    ta_courses
    :return: true if changes applied, false if course not in database add it through import course quota/ta cohort
    '''
    course_id = get_course_id(course_num)
    if course_id is None:
        return False

    user_id = find_user_id_by_name_and_school_id(fname,lname,student_id)

    # create an account then the user can register and we can add info
    if user_id is None:
        is_student = True
        is_prof = False
        if group == "instructor":
            is_student = False
            is_prof = True

        add_user(student_id, fname, lname, email, None, None, is_student, True, is_prof, False, False)
        user_id = find_user_id_by_name_and_school_id(fname, lname, student_id)

    # add to tas table if not in there
    query_ta = query_db(f"Select user_id FROM tas WHERE user_id = {user_id}")
    if query_ta is None:
        mutate_db('INSERT INTO tas VALUES (?)', [user_id])


    # add to ta_courses
    mutate_db('INSERT INTO ta_courses VALUES (?,?,?,?)', [user_id, course_id, course_term, hours])

    return True


def remove_ta(fname, lname, student_id, course_num, course_term):
    '''
    SQL for Remove TA to Course in the orange area TA administration
    Tables affected
    ta_courses
    :return:true if added
    '''
    user_id = find_user_id_by_name_and_school_id(fname,lname,student_id)
    course_id = get_course_id(course_num)
    mutate_db(f"DELETE FROM ta_courses WHERE user_id = {user_id} AND course_id = {course_id} AND course_term LIKE '{course_term}';")

    return True

