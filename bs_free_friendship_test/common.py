import uuid
import random
from typing import Any

from . import database
from . import static


def _error_select(err: database.sqlite3.Error) -> database.DatabaseError:
    return database.DatabaseError(err.sqlite_errorcode, f"Could not select from table: {err}")


def _error_insert(err: database.sqlite3.Error) -> database.DatabaseError:
    return database.DatabaseError(err.sqlite_errorcode, f"Could not insert into table: {err}")


def _error_update(err: database.sqlite3.Error) -> database.DatabaseError:
    return database.DatabaseError(err.sqlite_errorcode, f"Could not update table: {err}")


def _error_delete(err: database.sqlite3.Error) -> database.DatabaseError:
    return database.DatabaseError(err.sqlite_errorcode, f"Could not delete from table: {err}")


def _error_find_entity(id_: Any) -> database.DatabaseError:
    return database.DatabaseError(None, f"Could not find entity with ID {id_}")


def create_new_id() -> str:
    return str(uuid.uuid4().hex)


def get_form_answers(form) -> tuple[int, list[str]]:
    question_index = int(form["question_index"])
    answers = [str(static.G_QUESTIONS[question_index].answers.index(value)) for (key, value) in form.items() if key.startswith("question_answer")]

    return question_index, answers


def redirect_to_create_start(fl):
    return fl.redirect(fl.url_for("create._start", _method="GET"))


def create_new_quiz(creator_name: str) -> str:
    db = database.open_database()

    new_id = create_new_id()
    new_public_id = create_new_id()
    question_indices = list(map(str, range(len(static.G_QUESTIONS))))
    random.shuffle(question_indices)

    try:
        db.execute(
            "INSERT INTO Quiz (Id, PublicId, CreatorName, ShuffledQuestionIndices, CurrentQuestionIndex, CreationTimeStamp) "
            "VALUES (?, ?, ?, ?, ?, UNIXEPOCH())",
            (new_id, new_public_id, creator_name, ",".join(question_indices), 0)
        )
        db.commit()
    except db.Error as err:
        raise _error_insert(err)

    return new_id


def create_new_completed_quiz(friend_name: str, quiz_id: str) -> str:
    db = database.open_database()

    new_id = create_new_id()

    try:
        db.execute(
            "INSERT INTO CompletedQuiz (Id, FriendName, CurrentQuestionIndex, QuizId) VALUES (?, ?, ?, ?)",
            (new_id, friend_name, 0, quiz_id)
        )
        db.commit()
    except db.Error as err:
        raise _error_insert(err)

    return new_id


def get_quiz_id_from_public_id(public_quiz_id: str) -> str:
    db = database.open_database()

    try:
        result = db.execute("SELECT Id FROM Quiz WHERE PublicId = ?", (public_quiz_id,)).fetchone()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(public_quiz_id)

    return result[0]


def get_quiz_data(quiz_id: str) -> tuple[str, str, list[int], int]:
    db = database.open_database()

    try:
        result = db.execute("SELECT * FROM Quiz WHERE Id = ?", (quiz_id,)).fetchone()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(quiz_id)

    return result["PublicId"], result["CreatorName"], list(map(int, result["ShuffledQuestionIndices"].split(","))), result["CurrentQuestionIndex"]


def get_completed_quiz_data(completed_quiz_id: str) -> tuple[str, int, str]:
    db = database.open_database()

    try:
        result = db.execute("SELECT * FROM CompletedQuiz WHERE Id = ?", (completed_quiz_id,)).fetchone()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(completed_quiz_id)

    return result["FriendName"], result["CurrentQuestionIndex"], result["QuizId"]


def get_quiz_question_count(quiz_id: str) -> int:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT COUNT(*) FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId "
            "JOIN Quiz ON QuizQuestionAnswer.QuizId = Quiz.Id WHERE Quiz.Id = ?",
            (quiz_id,)
        ).fetchone()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(quiz_id)

    return result[0]


def get_completed_quiz_question_count(completed_quiz_id: str) -> int:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT COUNT(*) FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId "
            "JOIN CompletedQuiz ON CompletedQuizQuestionAnswer.CompletedQuizId = CompletedQuiz.Id WHERE CompletedQuiz.Id = ?",
            (completed_quiz_id,)
        ).fetchone()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(completed_quiz_id)

    return result[0]


def get_quiz_question_answer_indices(quiz_id: str) -> list[int]:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId "
            "JOIN Quiz ON QuizQuestionAnswer.QuizId = Quiz.Id WHERE Quiz.Id = ? ORDER BY QuestionIndex ASC",
            (quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(quiz_id)

    return list(map(lambda x: x[0], result))


def get_completed_quiz_question_answer_indices(completed_quiz_id: str) -> list[int]:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId "
            "JOIN CompletedQuiz ON CompletedQuizQuestionAnswer.CompletedQuizId = CompletedQuiz.Id WHERE CompletedQuiz.Id = ? ORDER BY QuestionIndex ASC",
            (completed_quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(completed_quiz_id)

    return list(map(lambda x: x[0], result))


def get_quiz_question_answers(quiz_id: str) -> list[tuple[int, list[int]]]:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex, AnswerIndices FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId "
            "JOIN Quiz ON QuizQuestionAnswer.QuizId = Quiz.Id WHERE Quiz.Id = ? ORDER BY QuestionIndex ASC",
            (quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(quiz_id)

    return list(map(lambda x: (x[0], list(map(int, x[1].split(",")))), result))


def get_completed_quiz_question_answers(completed_quiz_id: str) -> list[tuple[int, list[int]]]:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex, AnswerIndices FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId "
            "JOIN CompletedQuiz ON CompletedQuizQuestionAnswer.CompletedQuizId = CompletedQuiz.Id WHERE CompletedQuiz.Id = ? ORDER BY QuestionIndex ASC",
            (completed_quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(completed_quiz_id)

    return list(map(lambda x: (x[0], list(map(int, x[1].split(",")))), result))


def add_quiz_question_answer(quiz_id: str, question_index: int, answer_indices: list[str]):
    db = database.open_database()

    try:
        result = db.execute(
            "INSERT INTO QuestionAnswer (QuestionIndex, AnswerIndices) VALUES (?, ?) RETURNING Id",
            (question_index, ",".join(answer_indices))
        ).fetchone()
        db.execute("INSERT INTO QuizQuestionAnswer (QuizId, QuestionAnswerId) VALUES (?, ?)", (quiz_id, result[0]))
        db.commit()
    except db.Error as err:
        raise _error_insert(err)


def add_completed_quiz_question_answer(completed_quiz_id: str, question_index: int, answer_indices: list[str]):
    db = database.open_database()

    try:
        result = db.execute(
            "INSERT INTO QuestionAnswer (QuestionIndex, AnswerIndices) VALUES (?, ?) RETURNING Id",
            (question_index, ",".join(answer_indices))
        ).fetchone()
        db.execute("INSERT INTO CompletedQuizQuestionAnswer (CompletedQuizId, QuestionAnswerId) VALUES (?, ?)", (completed_quiz_id, result[0]))
        db.commit()
    except db.Error as err:
        raise _error_insert(err)


def next_quiz_question(quiz_id: str):
    _, _, shuffled_question_indices, current_question_index = get_quiz_data(quiz_id)
    current_question_indices = get_quiz_question_answer_indices(quiz_id)

    initial = current_question_index

    while True:
        current_question_index = (current_question_index + 1) % len(static.G_QUESTIONS)
        question_index = shuffled_question_indices[current_question_index]

        if question_index not in current_question_indices:
            _update_quiz_current_question_index(quiz_id, current_question_index)
            break

        if current_question_index == initial:
            break


def next_completed_quiz_question(completed_quiz_id: str):
    _, current_question_index, quiz_id = get_completed_quiz_data(completed_quiz_id)
    current_question_indices = get_completed_quiz_question_answer_indices(completed_quiz_id)
    question_indices = get_quiz_question_answer_indices(quiz_id)

    initial = current_question_index

    while True:
        current_question_index = (current_question_index + 1) % 20
        question_index = question_indices[current_question_index]

        if question_index not in current_question_indices:
            _update_completed_quiz_current_question_index(completed_quiz_id, current_question_index)
            break

        if current_question_index == initial:
            break


def _update_quiz_current_question_index(quiz_id: str, current_question_index: int):
    db = database.open_database()

    try:
        db.execute("UPDATE Quiz SET CurrentQuestionIndex = ? WHERE Id = ?", (current_question_index, quiz_id))
        db.commit()
    except db.Error as err:
        raise _error_update(err)


def _update_completed_quiz_current_question_index(completed_quiz_id: str, current_question_index: int):
    db = database.open_database()

    try:
        db.execute("UPDATE CompletedQuiz SET CurrentQuestionIndex = ? WHERE Id = ?", (current_question_index, completed_quiz_id))
        db.commit()
    except db.Error as err:
        raise _error_update(err)


def get_quiz_score(completed_quiz_id: str) -> float:
    _, _, quiz_id = get_completed_quiz_data(completed_quiz_id)

    quiz_question_answers = get_quiz_question_answers(quiz_id)
    completed_quiz_question_answers = get_completed_quiz_question_answers(completed_quiz_id)

    max_score = _get_quiz_max_score(quiz_question_answers)
    score = 0

    for question_answer in completed_quiz_question_answers:
        score += _get_quiz_question_score(question_answer, quiz_question_answers)

    assert score <= max_score

    return float(score * 100) / float(max_score)


def _get_quiz_max_score(quiz_question_answers: list[tuple[int, list[int]]]) -> int:
    max_score = 0

    for question_answer in quiz_question_answers:
        if static.G_QUESTIONS[question_answer[0]].single_type:
            max_score += 1
        else:
            max_score += len(question_answer[1])

    return max_score


def _get_quiz_question_score(completed_quiz_question_answer: tuple[int, list[int]], quiz_question_answers: list[tuple[int, list[int]]]) -> int:
    for question_answer in quiz_question_answers:
        if question_answer[0] != completed_quiz_question_answer[0]:
            continue

        if static.G_QUESTIONS[question_answer[0]].single_type:
            return int(question_answer[1][0] == completed_quiz_question_answer[1][0])
        else:
            score = 0
            for i in range(len(static.G_QUESTIONS[question_answer[0]].answers)):
                if i in question_answer[1] and i in completed_quiz_question_answer[1]:
                    score += 1
                elif not (i not in question_answer[1] and i not in completed_quiz_question_answer[1]):
                    score -= 1
            return max(score, 0)

    assert False


def get_quiz_completed_quizes(quiz_id: str) -> list[tuple[str, str]]:
    db = database.open_database()

    try:
        result = db.execute(
            "SELECT Id, FriendName FROM CompletedQuiz as InitialCompletedQuiz WHERE QuizId = ? AND "
            "(SELECT COUNT(*) FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId "
            "JOIN CompletedQuiz ON CompletedQuizQuestionAnswer.CompletedQuizId = CompletedQuiz.Id WHERE CompletedQuiz.Id = InitialCompletedQuiz.Id) = 20 "
            "ORDER BY FriendName ASC",
            (quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise _error_select(err)

    if result is None:
        raise _error_find_entity(quiz_id)

    return list(map(lambda x: (x[0], x[1]), result))


def delete_quizes_older_than(db: database.sqlite3.Connection, hours: int):
    try:
        db.execute("DELETE FROM Quiz WHERE UNIXEPOCH() - CreationTimeStamp > ?", (hours * 3600,))
        db.commit()
    except db.Error as err:
        raise _error_delete(err)
