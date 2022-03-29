CREATE TABLE user (
    user_id text PRIMARY KEY,
    first_name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL UNIQUE,
    category text NOT NULL,
    username text NOT NULL UNIQUE,
    password text NOT NULL
);

CREATE TABLE student (
    user_id text NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE course (
    course_id text PRIMARY KEY,
    course_name text NOT NULL
);

CREATE TABLE registered_courses (
    reg_course_id,
    user_id NOT NULL,
    course_id NOT NULL,
    PRIMARY KEY (reg_course_id),
    FOREIGN KEY (user_id) REFERENCES student (user_id),
    FOREIGN KEY (course_id) REFERENCES course (course_id)
);