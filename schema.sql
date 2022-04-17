CREATE TABLE users (
    user_id integer PRIMARY KEY,
    first_name text NOT NULL,
    last_name text NOT NULL,
    email text,
    username text,
    password text,
    location text,
    legal_name text,
    phone text,
    active integer NOT NULL  -- this is to tell if the user still have an account not for sessions
);

CREATE TABLE admins (
    user_id integer,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE sys_ops (
    user_id integer,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
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
    user_id integer,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE profs (
    user_id integer,
    prof_id integer,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
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
    user_id integer,
    course_id integer NOT NULL,
    course_term text NOT NULL,
    PRIMARY KEY (user_id, course_id, course_term),
    FOREIGN KEY (user_id) REFERENCES profs (user_id),
    FOREIGN KEY (course_id, course_term) REFERENCES course_terms (course_id, course_term)
);

CREATE TABLE ta_courses (
    user_id integer,
    course_id integer NOT NULL,
    course_term text NOT NULL,
    hours integer,
    PRIMARY KEY (user_id, course_id, course_term),
    FOREIGN KEY (user_id) REFERENCES tas (user_id),
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
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    course_term NOT NULL,
    rating integer NOT NULL,
    review_desc text,
    PRIMARY KEY (review_id),
    FOREIGN KEY (user_id) REFERENCES tas (user_id),
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
    FOREIGN KEY (prof_id) REFERENCES profs (user_id),
    FOREIGN KEY (ta_id) REFERENCES tas (user_id),
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
    FOREIGN KEY (prof_id) REFERENCES profs (user_id),
    FOREIGN KEY (ta_id) REFERENCES tas (user_id)
);

CREATE TABLE ta_cohort (
    cohort_id integer,
    user_id integer NOT NULL,
    priority BIT,
    hours integer,
    date_applied text,
    open_to_other_courses BIT,
    notes text,
    PRIMARY KEY (cohort_id),
    FOREIGN KEY (user_id) REFERENCES tas (user_id)
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
    session_id text,
    user_id integer,
    expiry_date text,
    last_activity text,
    PRIMARY KEY (session_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);