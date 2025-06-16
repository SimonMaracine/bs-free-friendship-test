DROP TABLE IF EXISTS Quiz;
DROP TABLE IF EXISTS CompletedQuiz;
DROP TABLE IF EXISTS QuestionAnswer;
DROP TABLE IF EXISTS QuizQuestionAnswer;
DROP TABLE IF EXISTS CompletedQuizQuestionAnswer;

DROP TRIGGER IF EXISTS AvoidDuplicateQuestionAnswers;
DROP TRIGGER IF EXISTS AvoidDuplicateCompletedQuestionAnswers;

DROP TRIGGER IF EXISTS DeleteQuiz;
DROP TRIGGER IF EXISTS DeleteCompletedQuiz;
DROP TRIGGER IF EXISTS DeleteQuizQuestionAnswer;
DROP TRIGGER IF EXISTS DeleteCompletedQuizQuestionAnswer;

DROP TRIGGER IF EXISTS SanitizeQuizInsert;
DROP TRIGGER IF EXISTS ValidateQuizInsert;
DROP TRIGGER IF EXISTS SanitizeCompletedQuizInsert;
DROP TRIGGER IF EXISTS ValidateCompletedQuizInsert;

CREATE TABLE Quiz (
    Id TEXT NOT NULL PRIMARY KEY,
    PublicId TEXT NOT NULL,  -- Not primary key
    CreatorName TEXT NOT NULL,
    ShuffledQuestionIndices TEXT NOT NULL,  -- Comma separated list of indices (20)
    CurrentQuestionIndex INTEGER NOT NULL,  -- Index in the shuffled list (20)
    CreationTimeStamp INTEGER NOT NULL
);

CREATE TABLE CompletedQuiz (
    Id TEXT NOT NULL PRIMARY KEY,
    FriendName TEXT NOT NULL,
    CurrentQuestionIndex INTEGER NOT NULL,  -- Index in the list (20)
    QuizId TEXT NOT NULL,

    FOREIGN KEY (QuizId) REFERENCES Quiz (Id)
);

CREATE TABLE QuestionAnswer (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    QuestionIndex INTEGER NOT NULL,
    AnswerIndices TEXT NOT NULL  -- Comma separated list of indices
);

CREATE TABLE QuizQuestionAnswer (
    QuizId TEXT NOT NULL,
    QuestionAnswerId INTEGER NOT NULL,

    PRIMARY KEY (QuizId, QuestionAnswerId),
    FOREIGN KEY (QuizId) REFERENCES Quiz (Id),
    FOREIGN KEY (QuestionAnswerId) REFERENCES QuestionAnswer (Id)
);

CREATE TABLE CompletedQuizQuestionAnswer (
    CompletedQuizId TEXT NOT NULL,
    QuestionAnswerId INTEGER NOT NULL,

    PRIMARY KEY (CompletedQuizId, QuestionAnswerId),
    FOREIGN KEY (CompletedQuizId) REFERENCES CompletedQuiz (Id),
    FOREIGN KEY (QuestionAnswerId) REFERENCES QuestionAnswer (Id)
);

CREATE TRIGGER IF NOT EXISTS AvoidDuplicateQuestionAnswers AFTER INSERT ON QuizQuestionAnswer
BEGIN
    SELECT CASE
        WHEN
            (
                SELECT COUNT(*) FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId
                WHERE QuizQuestionAnswer.QuizId = NEW.QuizId GROUP BY QuestionIndex HAVING COUNT(QuestionIndex) > 1
            ) > 1
        THEN
            RAISE(ABORT, "Duplicate question answer")
    END;
END;

CREATE TRIGGER IF NOT EXISTS AvoidDuplicateCompletedQuestionAnswers AFTER INSERT ON CompletedQuizQuestionAnswer
BEGIN
    SELECT CASE
        WHEN
            (
                SELECT COUNT(*) FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId
                WHERE CompletedQuizQuestionAnswer.CompletedQuizId = NEW.CompletedQuizId GROUP BY QuestionIndex HAVING COUNT(QuestionIndex) > 1
            ) > 1
        THEN
            RAISE(ABORT, "Duplicate question answer")
    END;
END;

CREATE TRIGGER IF NOT EXISTS DeleteQuiz BEFORE DELETE ON Quiz
BEGIN
    DELETE FROM QuizQuestionAnswer WHERE QuizId = OLD.Id;
    DELETE FROM CompletedQuiz WHERE QuizId = OLD.Id;
END;

CREATE TRIGGER IF NOT EXISTS DeleteCompletedQuiz BEFORE DELETE ON CompletedQuiz
BEGIN
    DELETE FROM CompletedQuizQuestionAnswer WHERE CompletedQuizId = OLD.Id;
END;

CREATE TRIGGER IF NOT EXISTS DeleteQuizQuestionAnswer BEFORE DELETE ON QuizQuestionAnswer
BEGIN
    DELETE FROM QuestionAnswer WHERE Id = OLD.QuestionAnswerId;
END;

CREATE TRIGGER IF NOT EXISTS DeleteCompletedQuizQuestionAnswer BEFORE DELETE ON CompletedQuizQuestionAnswer
BEGIN
    DELETE FROM QuestionAnswer WHERE Id = OLD.QuestionAnswerId;
END;

CREATE TRIGGER IF NOT EXISTS SanitizeQuizInsert AFTER INSERT ON Quiz
BEGIN
    UPDATE Quiz SET CreatorName = TRIM(NEW.CreatorName) WHERE Id = NEW.Id;
END;

CREATE TRIGGER IF NOT EXISTS ValidateQuizInsert BEFORE INSERT ON Quiz
BEGIN
    SELECT CASE
        WHEN LENGTH(TRIM(NEW.CreatorName)) NOT BETWEEN 1 AND 18
        THEN RAISE(ABORT, "Invalid name")
    END;
END;

CREATE TRIGGER IF NOT EXISTS SanitizeCompletedQuizInsert AFTER INSERT ON CompletedQuiz
BEGIN
    UPDATE CompletedQuiz SET FriendName = TRIM(NEW.FriendName) WHERE Id = NEW.Id;
END;

CREATE TRIGGER IF NOT EXISTS ValidateCompletedQuizInsert BEFORE INSERT ON CompletedQuiz
BEGIN
    SELECT CASE
        WHEN LENGTH(TRIM(NEW.FriendName)) NOT BETWEEN 1 AND 18
        THEN RAISE(ABORT, "Invalid name")
    END;
END;
