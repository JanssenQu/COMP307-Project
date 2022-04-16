from sqlalchemy import false
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


def get_first_value(query_result, col_name):
    if query_result is None:
        return None
    for values in query_result:
        return dict(values).get(col_name)
    return None


def add_course_quota_to_db(term_month_year, course_num, course_type, course_name,
instructor_name, course_enrollment_num, TA_quota):
    '''
    Add a row of CourseQuota.csv into the database
    Assumes that the instructor exists in the database
    Stores data about courses and instructor to be seen by the ta admin

    Tables affected: courses, teaching_courses, course_terms

    :param term_month_year: field from csv
    :param course_num: field from csv
    :param course_type: field from csv
    :param course_name: field from csv
    :param instructor_name: field from csv
    :param course_enrollment_num: field from csv
    :param TA_quota: field from csv
    :return: true if successfully added
    '''
    course_id = get_course_id(course_num)
    fname, lname = name_splitter(instructor_name)
    user_id_query = query_db(f"Select user_id FROM users WHERE first_name = '{fname}' AND last_name = '{lname}'")

    user_id = get_first_value(user_id_query,'user_id')

    if user_id:
        if not course_id:
            mutate_db("INSERT INTO courses VALUES (?, ?, ?, ?)", [None, course_name, course_num, course_type])
            course_id = get_course_id(course_num)

        already_teaching = query_db(f"Select user_id FROM teaching_courses WHERE user_id = {user_id} AND "
                                 f"course_id = {course_id} AND course_term = '{term_month_year}'")
        if not already_teaching:
            mutate_db("INSERT INTO teaching_courses VALUES (?, ?, ?)", [user_id, course_id, term_month_year])


        already_set = query_db(f"Select course_id FROM course_terms WHERE course_id = {course_id} AND "
                                 f"course_term = '{term_month_year}'")
        if not already_set:
            mutate_db("INSERT INTO course_terms VALUES (?, ?, ?, ?)", [course_id, term_month_year, int(course_enrollment_num), int(TA_quota)])
            return True
        else:
            mutate_db(f"UPDATE course_terms \n"
                      f"SET course_enroll_num = {int(course_enrollment_num)}, ta_quota = {int(TA_quota)} \n"
                      f"WHERE course_id = {course_id} AND course_term = '{term_month_year}' ")
            return True
    else:
        return False


def add_ta_cohort_to_db(term_month_year, TA_name, student_ID,
legal_name, email, grad_ugrad, supervisor_name, priority, hours, date_applied,
location, phone, degree, courses_applied_for, open_to_other_courses, notes):
    """
    Add a row of TACohort.csv into the database

    Assumes that the ta are students
    If no in db will register the ta into users, students, and tas

    Tables affected: users, students, tas, ta_cohort, ta_applied_courses

    Stores data about ta applicants to be seen by the ta admin
    :param term_month_year: field from csv
    :param TA_name: field from csv
    :param student_ID: field from csv
    :param legal_name: field from csv
    :param email: field from csv
    :param grad_ugrad: field from csv
    :param supervisor_name: field from csv
    :param priority: field from csv
    :param hours: field from csv
    :param date_applied: field from csv
    :param location: field from csv
    :param phone: field from csv
    :param degree: field from csv
    :param courses_applied_for: field from csv
    :param open_to_other_courses: field from csv
    :param notes: field from csv
    :return: true if successfully added
    """

    # see if user is in db
    fname, lname = name_splitter(TA_name)
    user_id_query = query_db(f"Select user_id FROM users "
                        f"WHERE first_name = '{fname}' AND last_name = '{lname}'")
    user_id = get_first_value(user_id_query,'user_id')

    # add if new
    if not user_id:
        add_user(student_ID, fname, lname, email, None, None, student=True, ta=True, prof=False, admin=False,
             sysop=False)
        user_id_query = query_db(f"Select user_id FROM users "
                                 f"WHERE first_name = '{fname}' AND last_name = '{lname}'")
        user_id = get_first_value(user_id_query, 'user_id')
    else:
        # updates the student to TA also updates the fields student_ID, fname, lname, email
        # change it to "" to leave student_ID, fname, lname, email as it was
        update_user(user_id, student_ID, fname, lname, email, "", "", True, True, False, False, False)

    # update the fields that were not supported by add_user() and update_user
    mutate_db(f"UPDATE users \n"
              f"SET legal_name = '{legal_name}', location = '{location}', phone = '{phone}' \n"
              f"WHERE user_id = {user_id} ")
    mutate_db(f"UPDATE students \n"
              f"SET grad_ugrad = '{grad_ugrad}', supervisor_name = '{supervisor_name}', degree = '{degree}' \n"
              f"WHERE user_id = {user_id} ")

    # turns yes/no string into bit
    bool_dict = {'yes': 1, 'no': 0}
    # see if already in cohort before adding
    already_applied_query = query_db(f"Select cohort_id FROM ta_cohort "
                                     f"WHERE user_id = {user_id} AND priority = {bool_dict[priority]} "
                                     f"AND hours = {hours} AND date_applied = '{date_applied}' AND "
                                     f"open_to_other_courses = {bool_dict[open_to_other_courses]} AND "
                                     f"notes = '{notes}'")
    in_cohort = get_first_value(already_applied_query, 'cohort_id')
    if not in_cohort:
        mutate_db("INSERT INTO ta_cohort VALUES (?, ?, ?, ?, ?, ?, ?)", [None, user_id, bool_dict[priority], hours, date_applied, bool_dict[open_to_other_courses], notes])

    query_cohort_id = query_db(f"Select cohort_id FROM ta_cohort "
                               f"WHERE user_id = {user_id} AND priority = {bool_dict[priority]} AND hours = {hours} "
                               f"AND date_applied = '{date_applied}' AND "
                               f"open_to_other_courses = {bool_dict[open_to_other_courses]} AND notes = '{notes}'")
    cohort_id = get_first_value(query_cohort_id,'cohort_id')

    courses = courses_applied_for.split(",")
    for course in courses:
        # take out spaces at start and end
        course_id = get_course_id(course.strip())
        # see if already in ta_applied_courses before adding
        already_applied_query = query_db(f"Select cohort_id FROM ta_applied_courses "
                                 f"WHERE cohort_id = {cohort_id} AND course_id = {course_id} AND course_term = '{term_month_year}'")
        already_applied = get_first_value(already_applied_query, 'cohort_id')
        if course_id and not already_applied:
            mutate_db("INSERT INTO ta_applied_courses VALUES (?, ?, ?)", [cohort_id, course_id, term_month_year])

    return True
