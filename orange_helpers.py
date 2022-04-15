from sqlalchemy import false
from blue_helpers import get_course_id
from database import *
from user_registration_and_yellow_helpers import name_splitter


def add_ta():
    '''
    SQL Add TA to Course in the orange area TA administration

    Tables affected
    tas
    ta_courses
    courses
    course_terms
    ta_cohort
    :return: true if changes applied
    '''

    return

def remove_ta():
    '''
    SQL for Remove TA to Course in the orange area TA administration


    Tables affected
    tas
    ta_courses
    courses
    course_terms
    ta_cohort
    :return: true if changes applied
    '''

    return

def add_course_quota_to_db(term_month_year, course_num, course_type, course_name, 
instructor_name, course_enrollment_num, TA_quota):
    course_id = get_course_id(course_num)
    fname, lname = name_splitter(instructor_name)
    user_id = query_db(f"Select user_id FROM users "
                        f"WHERE first_name = '{fname}' AND last_name = '{lname}'", one=True)
    if user_id:
        if not course_id:
            mutate_db("INSERT INTO courses VALUES (?, ?, ?, ?)", [None, course_name, course_num, course_type])
            course_id = get_course_id(course_num)
        mutate_db("INSERT INTO course_terms VALUES (?, ?, ?, ?)", [course_id, term_month_year, int(course_enrollment_num), int(TA_quota)])
        mutate_db("INSERT INTO teaching_courses VALUES (?, ?, ?)", [user_id, course_id, term_month_year])
        return True
    else:
        return False

def add_ta_cohort_to_db(term_month_year, TA_name, student_ID, 
legal_name, email, is_grad, supervisor_name, priority, hours, date_applied, 
location, phone, degree, courses_applied_for, open_to_other_courses, notes):
    return 


