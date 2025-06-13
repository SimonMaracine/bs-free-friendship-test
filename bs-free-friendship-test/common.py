import uuid
import random

from . import database
from . import glob


def valid_name(name: str) -> bool:
    return bool(name.strip())


def create_new_quiz(creator_name: str) -> str:
    db = database.get_database()
    new_id = str(uuid.uuid4().int)

    question_indices = list(map(str, range(len(glob.QUESTIONS))))
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


def create_new_completed_quiz(friend_name: str, quiz_id: str):
    db = database.get_database()

    try:
        db.execute("INSERT INTO CompletedQuiz (FriendName, QuizId) VALUES (?, ?)", (friend_name.strip(), quiz_id))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")


def get_quiz_data(quiz_id: str) -> tuple[str, list[int], int]:
    db = database.get_database()

    try:
        result = db.execute("SELECT * FROM Quiz WHERE Id = ?", (quiz_id,)).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {quiz_id}")

    return result["CreatorName"], list(map(int, result["ShuffledQuestionIndices"].split(","))), result["CurrentQuestionIndex"]


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


def get_quiz_question_indices(quiz_id: str) -> list[int]:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex FROM QuestionAnswer JOIN QuizQuestionAnswer ON QuestionAnswer.Id = QuizQuestionAnswer.QuestionAnswerId "
            "JOIN Quiz ON QuizQuestionAnswer.QuizId = Quiz.Id WHERE Quiz.Id = ?",
            (quiz_id,)
        ).fetchall()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {quiz_id}")

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


def next_quiz_question(quiz_id: str):
    _, shuffled_question_indices, current_question_index = get_quiz_data(quiz_id)
    question_indices = get_quiz_question_indices(quiz_id)

    while True:
        current_question_index = (current_question_index + 1) % len(glob.QUESTIONS)
        question_index = shuffled_question_indices[current_question_index]

        if question_index not in question_indices:
            update_quiz_current_question_index(quiz_id, current_question_index)
            break


def update_quiz_current_question_index(quiz_id: str, current_question_index: int):
    db = database.get_database()

    try:
        db.execute("UPDATE Quiz SET CurrentQuestionIndex = ? WHERE Id = ?", (current_question_index, quiz_id))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not update table: {err}")
