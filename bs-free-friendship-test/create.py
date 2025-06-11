import uuid
import random

import flask as fl

from . import glob
from . import database


g_blueprint = fl.Blueprint("create", __name__, url_prefix="/create")


def _pick_random_question_index(question_indices: list[int]) -> int:
    all_indices = set(range(0, len(glob.QUESTIONS) - 1))
    remaining_indices = all_indices - set(question_indices)

    return random.choice(list(remaining_indices))


def _create_new_form(name: str) -> str | None:
    db = database.get_database()
    new_id = str(uuid.uuid4().int)

    try:
        db.execute(
            "INSERT INTO form (id, name_) VALUES (?, ?)",
            (new_id, name)
        )
        db.commit()
    except db.Error as err:
        fl.flash(f"Could not insert into table: {err}")
        return None

    return new_id


def _get_form_name(form_id: str) -> str | None:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT * FROM form WHERE id = ?",
            (form_id,)
        ).fetchone()
    except db.Error as err:
        fl.flash(f"Could not select from table: {err}")
        return None

    if result is None:
        fl.flash(f"Could not find form with id {form_id}")
        return None

    return result["name_"]


def _get_form_question_count(form_id: str) -> int | None:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT COUNT(*) FROM question WHERE form_id = ?",
            (form_id,)
        ).fetchone()
    except db.Error as err:
        fl.flash(f"Could not select from table: {err}")
        return None

    if result is None:
        fl.flash(f"Could not find form with id {form_id}")
        return None

    return result[0]


def _get_form_question_indices(form_id: str) -> list[int] | None:
    db = database.get_database()

    try:
        result = db.execute(
            "SELECT index_ FROM question WHERE form_id = ?",
            (form_id,)
        ).fetchall()
    except db.Error as err:
        fl.flash(f"Could not select from table: {err}")
        return None

    if result is None:
        fl.flash(f"Could not find form with id {form_id}")
        return None

    return result


@g_blueprint.route("/start", methods=("GET", "POST"))
def _start():
    if fl.request.method == "POST":
        new_id = _create_new_form(fl.request.form["form_name"])

        if new_id is not None:
            return fl.redirect(fl.url_for("create._form", _method="GET", form_id=new_id))

    return fl.render_template("create/start.html")


@g_blueprint.route("/form/<form_id>", methods=("GET", "POST"))
def _form(form_id):
    if fl.request.method == "POST":
        # TODO insert answer

        print(fl.request.form)

    name = _get_form_name(form_id)
    question_count = _get_form_question_count(form_id)
    question_indices = _get_form_question_indices(form_id)

    if None in (name, question_count, question_indices):
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    if question_count == len(glob.QUESTIONS):
        return fl.redirect(fl.url_for("create._done", _method="GET", form_id=form_id))

    print(question_indices)

    index = _pick_random_question_index(question_indices)  # type: ignore

    return fl.render_template("create/form.html", name=name, question_count=question_count, question=glob.QUESTIONS[index], question_index=index)


@g_blueprint.route("/done/<form_id>")
def _done(form_id):
    return fl.render_template("create/done.html")
