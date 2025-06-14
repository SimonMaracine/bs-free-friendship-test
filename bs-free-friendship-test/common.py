import uuid
import random

from . import database
from . import static


def valid_name(name: str) -> bool:
    return bool(name.strip())


def get_form_answers(form) -> tuple[int, list[str]]:
    question_index = int(form["question_index"])
    answers = [str(static.G_QUESTIONS[question_index].answers.index(value)) for (key, value) in form.items() if key.startswith("question_answer")]

    return question_index, answers


def create_new_quiz(creator_name: str) -> str:
    db = database.get_database()

    new_id = str(uuid.uuid4().int)
    question_indices = list(map(str, range(len(static.G_QUESTIONS))))
    random.shuffle(question_indices)

    try:
        db.execute(
            "INSERT INTO Quiz (Id, CreatorName, ShuffledQuestionIndices, CurrentQuestionIndex) VALUES (?, ?, ?, ?)",
            (new_id, creator_name.strip(), ",".join(question_indices), 0)
        )
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")

    return new_id


def create_new_completed_quiz(friend_name: str, quiz_id: str) -> str:
    db = database.get_database()

    new_id = str(uuid.uuid4().int)

    try:
        db.execute(
            "INSERT INTO CompletedQuiz (Id, FriendName, CurrentQuestionIndex, QuizId) VALUES (?, ?, ?, ?)",
            (new_id, friend_name.strip(), 0, quiz_id)
        )
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")

    return new_id


def get_quiz_data(quiz_id: str) -> tuple[str, list[int], int]:
    db = database.get_database()

    try:
        result = db.execute("SELECT * FROM Quiz WHERE Id = ?", (quiz_id,)).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {quiz_id}")

    return result["CreatorName"], list(map(int, result["ShuffledQuestionIndices"].split(","))), result["CurrentQuestionIndex"]


def get_completed_quiz_data(completed_quiz_id: str) -> tuple[str, int, str]:
    db = database.get_database()

    try:
        result = db.execute("SELECT * FROM CompletedQuiz WHERE Id = ?", (completed_quiz_id,)).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {completed_quiz_id}")

    return result["FriendName"], result["CurrentQuestionIndex"], result["QuizId"]


def get_quiz_question_count(quiz_id: str) -> int:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT COUNT(*) FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId "
            "JOIN Quiz ON QuizQuestionAnswer.QuizId = Quiz.Id WHERE Quiz.Id = ?",
            (quiz_id,)
        ).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {quiz_id}")

    return result[0]


def get_completed_quiz_question_count(completed_quiz_id: str) -> int:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT COUNT(*) FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId "
            "JOIN CompletedQuiz ON CompletedQuizQuestionAnswer.CompletedQuizId = CompletedQuiz.Id WHERE CompletedQuiz.Id = ?",
            (completed_quiz_id,)
        ).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {completed_quiz_id}")

    return result[0]


def get_quiz_question_indices(quiz_id: str) -> list[int]:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId "
            "JOIN Quiz ON QuizQuestionAnswer.QuizId = Quiz.Id WHERE Quiz.Id = ? ORDER BY QuestionIndex ASC",
            (quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {quiz_id}")

    return list(map(lambda x: x[0], result))


def get_completed_quiz_question_indices(completed_quiz_id: str) -> list[int]:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex FROM QuestionAnswer JOIN CompletedQuizQuestionAnswer ON QuestionAnswer.Id = CompletedQuizQuestionAnswer.QuestionAnswerId "
            "JOIN CompletedQuiz ON CompletedQuizQuestionAnswer.CompletedQuizId = CompletedQuiz.Id WHERE CompletedQuiz.Id = ? ORDER BY QuestionIndex ASC",
            (completed_quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {completed_quiz_id}")

    return list(map(lambda x: x[0], result))


def add_quiz_question_answer(quiz_id: str, question_index: int, answer_indices: list[str]):
    db = database.get_database()

    try:
        result = db.execute(
            "INSERT INTO QuestionAnswer (QuestionIndex, AnswerIndices) VALUES (?, ?) RETURNING Id",
            (question_index, ",".join(answer_indices))
        ).fetchone()
        db.execute("INSERT INTO QuizQuestionAnswer (QuizId, QuestionAnswerId) VALUES (?, ?)", (quiz_id, result[0]))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")


def add_completed_quiz_question_answer(completed_quiz_id: str, question_index: int, answer_indices: list[str]):
    db = database.get_database()

    try:
        result = db.execute(
            "INSERT INTO QuestionAnswer (QuestionIndex, AnswerIndices) VALUES (?, ?) RETURNING Id",
            (question_index, ",".join(answer_indices))
        ).fetchone()
        db.execute("INSERT INTO CompletedQuizQuestionAnswer (CompletedQuizId, QuestionAnswerId) VALUES (?, ?)", (completed_quiz_id, result[0]))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")


def next_quiz_question(quiz_id: str):
    _, shuffled_question_indices, current_question_index = get_quiz_data(quiz_id)
    current_question_indices = get_quiz_question_indices(quiz_id)

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
    current_question_indices = get_completed_quiz_question_indices(completed_quiz_id)
    question_indices = get_quiz_question_indices(quiz_id)

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
    db = database.get_database()

    try:
        db.execute("UPDATE Quiz SET CurrentQuestionIndex = ? WHERE Id = ?", (current_question_index, quiz_id))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not update table: {err}")


def _update_completed_quiz_current_question_index(completed_quiz_id: str, current_question_index: int):
    db = database.get_database()

    try:
        db.execute("UPDATE CompletedQuiz SET CurrentQuestionIndex = ? WHERE Id = ?", (current_question_index, completed_quiz_id))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not update table: {err}")
