from database import *
from blue_helpers import *


def get_course_id(course_num):
    course_id = None
    query_course_ids = query_db(f"Select course_id FROM courses WHERE course_num = '{course_num}'")
    for value in query_course_ids:
        course_id = dict(value).get("course_id")
    return course_id

def get_courses_with_tas():
    course_ids = []
    course_nums = []
    query_course_ids = query_db(f"Select DISTINCT course_id FROM ta_courses")
    for value in query_course_ids:
        course_ids.append(dict(value).get("course_id"))

    for course_id in course_ids:
        query_course_nums = query_db(f"Select course_num FROM courses WHERE course_id = {course_id}")
        for value in query_course_nums:
            course_nums.append(dict(value).get("course_num"))

    return sorted(course_nums)


def get_terms_with_tas(course_num):
    course_id = get_course_id(course_num)
    term_list = []
    query_terms = query_db(f"Select DISTINCT course_term FROM ta_courses WHERE course_id = {course_id}")
    for value in query_terms:
        term_list.append(dict(value).get("course_term"))

    return term_list


def get_tas(course_num,course_term):
    '''
    Get the list for the tas in a course for a term
    :param course_id: int course id of the course for which will be selected in the dropdown
    :param course_term: str name of the course term
    :return: list of tas in a course during a term
    '''
    course_id = get_course_id(course_num)

    ta_id_dict = query_db(f"Select user_id FROM ta_courses "
             f"WHERE course_id = '{course_id}' AND course_term = '{course_term}'")

    ta_id_list = []
    for value in ta_id_dict:
        ta_id_list.append(dict(value).get("user_id"))

    ta_name_list = []
    for id in ta_id_list:
        ta_name_dict = query_db(f"Select first_name,last_name FROM users WHERE user_id = '{id}'")
        for value in ta_name_dict:
            ta_name_list.append(f"{dict(value).get('first_name')} {dict(value).get('last_name')}")

    return ta_name_list


def insert_ta_rating(ta_name,course_num,term,stars,comment):
    course_id = get_course_id(course_num)
    ta_id = find_ta_id(ta_name, course_id, term)

    mutate_db('INSERT INTO ta_reviews VALUES (?,?,?,?,?,?)', [None, ta_id, course_id, term, int(stars), comment])
    return True

