import uuid
import random

import flask as fl

from . import glob
from . import database


g_blueprint = fl.Blueprint("create", __name__, url_prefix="/create")


def _create_new_form(creator_name: str) -> str:
    db = database.get_database()
    new_id = str(uuid.uuid4().int)

    question_indices = list(map(str, range(len(glob.QUESTIONS))))
    random.shuffle(question_indices)

    try:
        db.execute(
            "INSERT INTO Form (Id, CreatorName, ShuffledQuestionIndices, CurrentQuestionIndex) VALUES (?, ?, ?, ?)",
            (new_id, creator_name, ",".join(question_indices), 0)
        )
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")

    return new_id


def _get_form_data(form_id: str) -> tuple[str, list[int], int]:
    db = database.get_database()

    try:
        result = db.execute("SELECT * FROM Form WHERE Id = ?", (form_id,)).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {form_id}")

    return result["CreatorName"], list(map(int, result["ShuffledQuestionIndices"].split(","))), result["CurrentQuestionIndex"]


def _get_form_question_count(form_id: str) -> int:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT COUNT(*) FROM QuestionAnswer JOIN FormQuestionAnswer ON QuestionAnswer.Id = FormQuestionAnswer.QuestionAnswerId "
            "JOIN Form ON FormQuestionAnswer.FormId = Form.Id WHERE Form.Id = ?",
            (form_id,)
        ).fetchone()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find entity with id {form_id}")

    return result[0]


def _get_form_question_indices(form_id: str) -> list[int]:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT QuestionIndex FROM QuestionAnswer JOIN FormQuestionAnswer ON QuestionAnswer.Id = FormQuestionAnswer.QuestionAnswerId "
            "JOIN Form ON FormQuestionAnswer.FormId = Form.Id WHERE Form.Id = ?",
            (form_id,)
        ).fetchall()
    except db.Error as err:
        raise database.DatabaseError(f"Could not select from table: {err}")

    if result is None:
        raise database.DatabaseError(f"Could not find form with id {form_id}")

    return list(map(lambda x: x[0], result))


def _add_form_question_answer(form_id: str, question_index: int, answer_indices: list[str]):
    db = database.get_database()

    try:
        result = db.execute(
            "INSERT INTO QuestionAnswer (QuestionIndex, AnswerIndices) VALUES (?, ?) RETURNING Id",
            (question_index, ",".join(answer_indices))
        ).fetchone()
        db.execute("INSERT INTO FormQuestionAnswer (FormId, QuestionAnswerId) VALUES (?, ?)", (form_id, result[0]))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not insert into table: {err}")


def _next_form_question(form_id: str):
    _, shuffled_question_indices, current_question_index = _get_form_data(form_id)
    question_indices = _get_form_question_indices(form_id)

    while True:
        current_question_index = (current_question_index + 1) % len(glob.QUESTIONS)
        question_index = shuffled_question_indices[current_question_index]

        if question_index not in question_indices:
            _update_form_current_question_index(form_id, current_question_index)
            break


def _update_form_current_question_index(form_id: str, current_question_index: int):
    db = database.get_database()

    try:
        db.execute("UPDATE Form SET CurrentQuestionIndex = ? WHERE Id = ?", (current_question_index, form_id))
        db.commit()
    except db.Error as err:
        raise database.DatabaseError(f"Could not update table: {err}")


@g_blueprint.route("/start", methods=("GET", "POST"))
def _start():
    if fl.request.method == "POST":
        try:
            form_id = _create_new_form(fl.request.form["creator_name"])
        except database.DatabaseError as err:
            fl.flash(str(err))
        else:
            return fl.redirect(fl.url_for("create._form", _method="GET", form_id=form_id))

    return fl.render_template("create/start.html")


@g_blueprint.route("/form/<form_id>", methods=("GET", "POST"))
def _form(form_id):
    if fl.request.method == "POST":
        print(fl.request.form)

        question_index = int(fl.request.form["question_index"])
        answers = [str(glob.QUESTIONS[question_index].answers.index(value)) for (key, value) in fl.request.form.items() if key.startswith("question_answer")]

        if not answers:
            fl.flash("You must either submit an answer or skip the question")
        else:
            try:
                _add_form_question_answer(form_id, question_index, answers)
                _next_form_question(form_id)
            except database.DatabaseError as err:
                fl.flash(str(err))

    try:
        creator_name, shuffled_question_indices, current_question_index = _get_form_data(form_id)
        question_count = _get_form_question_count(form_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    if question_count == 20:
        return fl.redirect(fl.url_for("create._done", _method="GET", form_id=form_id))

    return fl.render_template(
        "create/form.html",
        creator_name=creator_name,
        question_count=question_count,
        question=glob.QUESTIONS[shuffled_question_indices[current_question_index]],
        question_index=shuffled_question_indices[current_question_index],
        form_id=form_id
    )


@g_blueprint.route("/form/<form_id>/skip", methods=("POST",))
def _form_skip(form_id):
    try:
        _next_form_question(form_id)
    except database.DatabaseError as err:
        fl.flash(str(err))

    return fl.redirect(fl.url_for("create._form", _method="GET", form_id=form_id))


@g_blueprint.route("/done/<form_id>")
def _done(form_id):
    return fl.render_template("create/done.html", form_id=form_id)
