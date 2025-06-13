DROP TABLE IF EXISTS Quiz;
DROP TABLE IF EXISTS CompletedQuiz;
DROP TABLE IF EXISTS QuestionAnswer;
DROP TABLE IF EXISTS QuizQuestionAnswer;
DROP TABLE IF EXISTS CompletedQuizQuestionAnswer;

CREATE TABLE Quiz (
    Id TEXT NOT NULL PRIMARY KEY,
    CreatorName TEXT NOT NULL,
    ShuffledQuestionIndices TEXT NOT NULL,  -- Comma separated list of indices
    CurrentQuestionIndex INTEGER NOT NULL  -- Index in the shuffled array
);

CREATE TABLE CompletedQuiz (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    FriendName TEXT NOT NULL,
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
    CompletedQuizId INTEGER NOT NULL,
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
END
