from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()
 
class User(db.Model):
    __tablename__ = 'user'
 
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String())
    username = db.Column(db.String())
    password = db.Column(db.String())
 
    def __init__(self, first_name, last_name, email, username, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = password

class Course(db.Model):
    __tablename__ = 'course'
 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String())
 
    def __init__(self, name):
        self.name = name

class RegisteredCourses(db.Model):
    __tablename__ = 'registeredcourses'
 
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer())
    course_id = db.Column(db.Integer())
 
    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id
        