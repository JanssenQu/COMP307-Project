from database import *
from session import *


# returns the course id of the selected course in the dropdown in select course to be passed in the url
def get_course_id(course_num):
    query = query_db(f"Select course_id FROM courses WHERE course_num = '{course_num}'")
    course_id = None
    for value in query:
        course_id = dict(value).get("course_id")
    return course_id


# below is for select course

# currently using get_all_courses() for select course
# we might use get_courses(session_id) instead if we want to use get_courses(session_id)
def get_all_courses():
    query = query_db(f"Select course_name, course_num FROM courses ")
    course_num_list = []
    for value in query:
        course_num = dict(value).get("course_num")
        course_num_list.append(course_num)
    return course_num_list


# work on it later if needed
# not tested might replace get_all_courses() might want to change return type to tuples or dict
def get_courses(session_id):
    user_id = get_user_id(session_id)
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
    for course_id in course_id_list: # append the course_num
        return

    return course_id_list, course_num_list