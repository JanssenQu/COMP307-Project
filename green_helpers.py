from database import *


# dict course_num, dict terms, list of ta
def create_form():
    form = {}
    classes = get_all_classes()
    for item in classes:
        term_dict = {}
        course_id = item.get("course_id")
        course_num = item.get("course_num")
        terms = get_terms(course_id)
        for course_term in terms:
            term_dict[course_term] = get_ta(course_id, course_term)
        form[course_num] = term_dict
    return form


def get_all_classes():
    query = query_db(f"Select course_id, course_name, course_num FROM courses ")
    course = []
    for value in query:
        course.append((dict(value)))
    return course


def get_terms(course_id):
    term_dict = query_db(f"Select * FROM course_terms WHERE course_id = {course_id}")
    term_list = []
    for value in term_dict:
        term_list.append(dict(value).get("course_term"))
    return term_list


def get_ta(course_id,course_term):
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


def insert_ta_rating(ta,course_num,term,stars,comment):
    query = query_db(f"Select course_id FROM courses WHERE course_num = {course_num}")
    course_id = None
    for value in query:
        course_id = dict(value).get("course_id")

    mutate_db('INSERT INTO ta_reviews VALUES (?,?,?,?,?,?)', [None, ta, int(course_id), term, int(stars), comment])
    return True

def script_string(data):
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

