DROP TABLE IF EXISTS Form;
DROP TABLE IF EXISTS CompletedForm;
DROP TABLE IF EXISTS QuestionAnswer;
DROP TABLE IF EXISTS FormQuestionAnswer;
DROP TABLE IF EXISTS CompletedFormQuestionAnswer;

CREATE TABLE Form (
    Id TEXT NOT NULL PRIMARY KEY,
    CreatorName TEXT NOT NULL
);

CREATE TABLE CompletedForm (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    FriendName TEXT NOT NULL,
    FormId TEXT NOT NULL PRIMARY KEY,

    FOREIGN KEY (FormId) REFERENCES Form (Id)
);

CREATE TABLE QuestionAnswer (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    QuestionIndex INTEGER NOT NULL,
    AnswerIndices TEXT NOT NULL  -- Comma separated list of indices
);

CREATE TABLE FormQuestionAnswer (
    FormId TEXT NOT NULL PRIMARY KEY,
    QuestionAnswerId INTEGER NOT NULL PRIMARY KEY,

    FOREIGN KEY (FormId) REFERENCES Form (Id),
    FOREIGN KEY (QuestionAnswerId) REFERENCES QuestionAnswer (Id)
);

CREATE TABLE CompletedFormQuestionAnswer (
    CompletedFormId INTEGER NOT NULL PRIMARY KEY,
    QuestionAnswerId INTEGER NOT NULL PRIMARY KEY,

    FOREIGN KEY (CompletedFormId) REFERENCES CompletedForm (Id),
    FOREIGN KEY (QuestionAnswerId) REFERENCES QuestionAnswer (Id)
);
