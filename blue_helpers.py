from database import *


def get_course_id(course_num):
    query = query_db(f"Select course_id FROM courses WHERE course_num = '{course_num}'")
    course_id = None
    for value in query:
        course_id = dict(value).get("course_id")
    return course_id


def get_all_courses():
    query = query_db(f"Select course_name, course_num FROM courses ")
    course_num_list = []
    for value in query:
        course_num = dict(value).get("course_num")
        course_num_list.append(course_num)
    return course_num_list


def get_courses(session_id):
    query_id = query_db(f"Select user_id FROM sessions WHERE session_id = '{session_id}' ")
    user_id = None
    for value in query_id:
        user_id = dict(value).get("user_id")


    course_id_list = []

    query_teaching_courses = query_db(f"Select course_id FROM teaching_courses WHERE user_id = '{user_id}'")
    for value in query_teaching_courses:
        course_id = dict(value).get("course_id")
        if course_id not in course_id_list:
            course_id_list.append(course_id)

    query_ta_courses = query_db(f"Select course_id FROM ta_courses WHERE user_id = '{user_id}'")
    for value in query_ta_courses:
        course_id = dict(value).get("course_id")
        if course_id not in course_id_list:
            course_id_list.append(course_id)

    course_num_list = []
    for course_id in course_id_list:
        return
    return