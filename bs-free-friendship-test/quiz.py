import flask as fl

from . import database
from . import common


g_blueprint = fl.Blueprint("quiz", __name__, url_prefix="/quiz")


@g_blueprint.route("/start/<quiz_id>", methods=("GET", "POST"))
def _start(quiz_id):
    if fl.request.method == "POST":
        friend_name = fl.request.form["friend_name"]

        if not common.valid_name(friend_name):
            fl.flash("Invalid name")
        else:
            try:
                common.create_new_completed_quiz(friend_name, quiz_id)
            except database.DatabaseError as err:
                fl.flash(str(err))
            else:
                return fl.redirect(fl.url_for("quiz._form", _method="GET", quiz_id=quiz_id))

    try:
        question_count = common.get_quiz_question_count(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    if question_count < 20:
        fl.flash("Quiz not ready")
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    creator_name, _, _ = common.get_quiz_data(quiz_id)

    return fl.render_template("quiz/start.html", creator_name=creator_name)


@g_blueprint.route("/form", methods=("GET", "POST"))
def _form():
    if fl.request.method == "POST":
        print("post")

    return fl.render_template("quiz/form.html")
