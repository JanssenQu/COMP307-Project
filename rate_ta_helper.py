from database import *

# probably going to redo all except maybe insert_ta_rating


def insert_ta_rating(ta_user_id,course_num,term,stars,comment):
    '''
    Adds the rating of the ta into the datasbase table ta_reviews
    :param ta_user_id: int database user_id of the ta not their
    :param course_num:
    :param term:
    :param stars:
    :param comment:
    :return: True if operation is complete
    '''
    query = query_db(f"Select course_id FROM courses WHERE course_num = {course_num}")
    course_id = None
    for value in query:
        course_id = dict(value).get("course_id")

    mutate_db('INSERT INTO ta_reviews VALUES (?,?,?,?,?,?)', [None, ta, int(course_id), term, int(stars), comment])
    return True



def get_terms(course_id):
    '''
    Get the list for term for when the class with id in the db == course_id
    :param course_id: int course id of the course for which will be selected in the dropdown
    :return: list of term for when the class is offered
    '''
    term_dict = query_db(f"Select * FROM course_terms WHERE course_id = {course_id}")
    term_list = []
    for value in term_dict:
        term_list.append(dict(value).get("course_term"))
    return term_list



def get_ta(course_id,course_term):
    '''
    Get the list for the tas in a course for a term
    :param course_id: int course id of the course for which will be selected in the dropdown
    :param course_term: str name of the course term
    :return: list of tas in a course during a term
    '''
    ta_id_dict = query_db(f"Select user_id FROM ta_courses "
             f"WHERE course_id = '{course_id}' AND course_term = '{course_term}'")

    ta_id_list = []
    for value in ta_id_dict:
        ta_id_list.append(dict(value).get("user_id"))

    ta_name_list = []
    for id in ta_id_list:
        ta_name_dict = query_db(f"Select first_name,last_name FROM users WHERE user_id = '{id}'")
        for value in ta_name_dict:
            ta_name_list.append((dict(value).get("first_name"), dict(value).get("last_name")))

    return ta_name_list



def rate_ta_dependent_dropdown_script():
    '''
    Work in progress might delete as it does not seem possible to inject a script into html
    Suppose to populate the dependent dropdowns
    '''
    data = {}

    query = query_db(f"Select course_id, course_name, course_num FROM courses ")
    classes = []
    for value in query:
        classes.append((dict(value)))

    for item in classes:
        term_dict = {}
        course_id = item.get("course_id")
        course_num = item.get("course_num")
        terms = get_terms(course_id)
        for course_term in terms:
            term_dict[course_term] = get_ta(course_id, course_term)
        data[course_num] = term_dict

    script = (f'<script>\n' \
                f'var courseObject = {data};\n' \
                f'document.getElementById("demo").innerHTML = courseObject;\n' \
                f'window.onload = function() {{\n' \
                f'var courseSel = document.getElementById("course");\n' \
                f'var termSel = document.getElementById("term");\n' \
                f'var taSel = document.getElementById("ta");' \
                f'for (var x in courseObject) {{\n' \
                f'courseSel.options[courseSel.options.length] = new Option(x, x);}}\n' \
                f'courseSel.onchange = function() {{\n' \
                f'taSel.length = 1;\n'
                f'termSel.length = 1;\n'
                f'for (var y in courseObject[this.value]) {{\n'
                f'termSel.options[termSel.options.length] = new Option(y, y);}}\n'
                f'}}\n'
                f'termSel.onchange = function() {{\n'
                f'taSel.length = 1;\n'
                f'var z = courseObject[courseSel.value][this.value];\n'
                f'for (var i = 0; i < z.length; i++) {{\n'
                f'for (var i = 0; i < z.length; i++) {{\n'
                f'taSel.options[taSel.options.length] = new Option(z[i], z[i]);}}\n'
                f'}}\n'
                f'}}\n'
                f'</script>')

    return script

