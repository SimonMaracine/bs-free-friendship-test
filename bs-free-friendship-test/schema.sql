DROP TABLE IF EXISTS form;
DROP TABLE IF EXISTS question;
DROP TABLE IF EXISTS answer;

CREATE TABLE form (
    id TEXT NOT NULL PRIMARY KEY,
    name_ TEXT NOT NULL
);

CREATE TABLE question (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    index_ INTEGER NOT NULL,
    question TEXT NOT NULL,
    question_test TEXT NOT NULL,
    single_type BOOLEAN NOT NULL,
    answers TEXT NOT NULL,
    form_id TEXT NOT NULL,

    FOREIGN KEY (form_id) REFERENCES form (id)
);

CREATE TABLE answer (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    answer TEXT NOT NULL,
    question_id INTEGER NOT NULL,

    FOREIGN KEY (question_id) REFERENCES question (id)
);
