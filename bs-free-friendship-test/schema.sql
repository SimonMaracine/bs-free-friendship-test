DROP TABLE IF EXISTS Form;
DROP TABLE IF EXISTS CompletedForm;
DROP TABLE IF EXISTS QuestionAnswer;
DROP TABLE IF EXISTS FormQuestionAnswer;
DROP TABLE IF EXISTS CompletedFormQuestionAnswer;

CREATE TABLE Form (
    Id TEXT NOT NULL PRIMARY KEY,
    CreatorName TEXT NOT NULL,
    ShuffledQuestionIndices TEXT NOT NULL,  -- Comma separated list of indices
    CurrentQuestionIndex INTEGER NOT NULL  -- Index in the shuffled array
);

CREATE TABLE CompletedForm (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    FriendName TEXT NOT NULL,
    FormId TEXT NOT NULL,

    FOREIGN KEY (FormId) REFERENCES Form (Id)
);

CREATE TABLE QuestionAnswer (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    QuestionIndex INTEGER NOT NULL,
    AnswerIndices TEXT NOT NULL  -- Comma separated list of indices
);

CREATE TABLE FormQuestionAnswer (
    FormId TEXT NOT NULL,
    QuestionAnswerId INTEGER NOT NULL,

    PRIMARY KEY (FormId, QuestionAnswerId),
    FOREIGN KEY (FormId) REFERENCES Form (Id),
    FOREIGN KEY (QuestionAnswerId) REFERENCES QuestionAnswer (Id)
);

CREATE TABLE CompletedFormQuestionAnswer (
    CompletedFormId INTEGER NOT NULL,
    QuestionAnswerId INTEGER NOT NULL,

    PRIMARY KEY (CompletedFormId, QuestionAnswerId),
    FOREIGN KEY (CompletedFormId) REFERENCES CompletedForm (Id),
    FOREIGN KEY (QuestionAnswerId) REFERENCES QuestionAnswer (Id)
);

CREATE TRIGGER IF NOT EXISTS AvoidDuplicateQuestionAnswers AFTER INSERT ON FormQuestionAnswer
BEGIN
    SELECT CASE
        WHEN
            (
                SELECT COUNT(*) FROM QuestionAnswer JOIN FormQuestionAnswer ON QuestionAnswer.Id = FormQuestionAnswer.QuestionAnswerId
                WHERE FormQuestionAnswer.FormId = NEW.FormId GROUP BY QuestionIndex HAVING COUNT(QuestionIndex) > 1
            ) > 1
        THEN
            RAISE(ABORT, "Duplicate question answer")
    END;
END
