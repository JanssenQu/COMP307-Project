CREATE TABLE users (
    user_id integer PRIMARY KEY,
    first_name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL UNIQUE,
    username text NOT NULL UNIQUE,
    password text NOT NULL,
    location text,
    legal_name text,
    phone text
);

CREATE TABLE admins (
    admin_id integer,
    PRIMARY KEY (admin_id),
    FOREIGN KEY (admin_id) REFERENCES users (user_id)
);

CREATE TABLE sys_ops (
    sysop_id integer,
    PRIMARY KEY (sysop_id),
    FOREIGN KEY (sysop_id) REFERENCES users (user_id)
);

CREATE TABLE students (
    user_id integer,
    student_id integer,
    grad BIT,
    supervisor_name text,
    degree text,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE tas (
    ta_id integer,
    PRIMARY KEY (ta_id),
    FOREIGN KEY (ta_id) REFERENCES students (user_id)
);

CREATE TABLE profs (
    prof_id integer,
    PRIMARY KEY (prof_id),
    FOREIGN KEY (prof_id) REFERENCES users (user_id)
);

CREATE TABLE courses (
    course_id integer PRIMARY KEY,
    course_name text NOT NULL,
    course_num text NOT NULL,
    course_type text NOT NULL
);

CREATE TABLE course_terms (
    course_id integer,
    course_term text NOT NULL,
    PRIMARY KEY (course_id, course_term),
    FOREIGN KEY (course_id) REFERENCES courses (course_id)
);

CREATE TABLE teaching_courses (
    prof_id integer,
    course_id integer NOT NULL,
    course_term text NOT NULL,
    PRIMARY KEY (prof_id, course_id, course_term),
    FOREIGN KEY (prof_id) REFERENCES profs (prof_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE ta_courses (
    ta_id integer,
    course_id integer NOT NULL,
    course_term text NOT NULL,
    PRIMARY KEY (ta_id, course_id, course_term),
    FOREIGN KEY (ta_id) REFERENCES tas (ta_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE registered_courses (
    user_id integer,
    course_id integer NOT NULL,
    course_term text NOT NULL,
    PRIMARY KEY (user_id, course_id, course_term),
    FOREIGN KEY (user_id) REFERENCES students (user_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE ta_reviews (
    review_id integer,
    ta_id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    course_term NOT NULL,
    rating integer NOT NULL,
    review_desc text,
    PRIMARY KEY (review_id),
    FOREIGN KEY (ta_id) REFERENCES ta_reviews (ta_id),
    FOREIGN KEY (user_id) REFERENCES students (user_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE ta_performance_log (
    log_id integer,
    prof_id integer NOT NULL,
    ta_id integer NOT NULL,
    course_id integer NOT NULL,
    course_term text NOT NULL,
    comment text NOT NULL,
    PRIMARY KEY (log_id),
    FOREIGN KEY (prof_id) REFERENCES profs (prof_id),
    FOREIGN KEY (ta_id) REFERENCES tas (ta_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE ta_wish_list (
    wish_id integer,
    course_id integer NOT NULL,
    course_term NOT NULL,
    prof_id NOT NULL,
    ta_id integer NOT NULL,
    PRIMARY KEY (wish_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term),
    FOREIGN KEY (prof_id) REFERENCES profs (prof_id),
    FOREIGN KEY (ta_id) REFERENCES tas (ta_id)
);

CREATE TABLE ta_cohort (
    cohort_id integer,
    ta_id integer NOT NULL,
    priority BIT,
    hours integer,
    date_applied text,
    open_to_other_courses BIT,
    notes text,
    PRIMARY KEY (cohort_id),
    FOREIGN KEY (ta_id) REFERENCES tas (ta_id)
);

CREATE TABLE ta_applied_courses (
    cohort_id integer,
    course_id integer,
    course_term text,
    PRIMARY KEY (cohort_id, course_id, course_term),
    FOREIGN KEY (cohort_id) REFERENCES ta_cohort (cohort_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE sessions (
    session_id integer,
    user_id integer,
    session_start text,
    session_expiry text,
    logged_in BIT,
    PRIMARY KEY (session_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);