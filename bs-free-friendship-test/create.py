import uuid

import flask as fl

from . import glob
from . import database

g_blueprint = fl.Blueprint("create", __name__, url_prefix="/create")


def _create_new_form(name: str) -> str | None:
    db = database.get_database()
    new_id = uuid.uuid4()

    try:
        db.execute(
            "INSERT INTO form (id, name_) VALUES (?, ?)",
            (str(new_id.int), name)
        )
        db.commit()
    except db.Error as err:
        fl.flash(f"Could not insert into form: {err}")
        return None

    return str(new_id.int)


def _get_form_name(form_id: str) -> str | None:
    db = database.get_database()

    try:
        form = db.execute(
            "SELECT * FROM form WHERE id = ?",
            (form_id,)
        ).fetchone()
    except db.Error as err:
        fl.flash(f"Could not select from form: {err}")
        return None

    if form is None:
        fl.flash("Could not find the requested entity")
        return None

    return form["name_"]


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
        # TODO next question

        return fl.redirect(fl.url_for("create._done", _method="GET", form_id=form_id))

    form_name = _get_form_name(form_id)

    if form_name is None:
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    return fl.render_template("create/form.html", name=form_name, question=glob.QUESTIONS[0])


@g_blueprint.route("/done/<form_id>")
def _done(form_id):
    return fl.render_template("create/done.html")
