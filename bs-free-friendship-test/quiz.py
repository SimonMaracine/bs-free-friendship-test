import flask as fl

from . import database
from . import static
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
                completed_quiz_id = common.create_new_completed_quiz(friend_name, quiz_id)
            except database.DatabaseError as err:
                fl.flash(str(err))
            else:
                return fl.redirect(fl.url_for("quiz._form", _method="GET", quiz_id=quiz_id, completed_quiz_id=completed_quiz_id))

    try:
        question_count = common.get_quiz_question_count(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    if question_count < 20:
        fl.flash("Quiz not ready")
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    try:
        creator_name, _, _ = common.get_quiz_data(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    return fl.render_template("quiz/start.html", creator_name=creator_name)


@g_blueprint.route("/form/<completed_quiz_id>", methods=("GET", "POST"))
def _form(completed_quiz_id):
    if fl.request.method == "POST":
        print(fl.request.form)

        question_index, answers = common.get_form_answers(fl.request.form)

        if not answers:
            fl.flash("You must either submit an answer or skip the question")
        else:
            try:
                common.add_completed_quiz_question_answer(completed_quiz_id, question_index, answers)
                common.next_completed_quiz_question(completed_quiz_id)
            except database.DatabaseError as err:
                fl.flash(str(err))

    try:
        friend_name, current_question_index, quiz_id = common.get_completed_quiz_data(completed_quiz_id)
        creator_name, _, _ = common.get_quiz_data(quiz_id)
        question_count = common.get_completed_quiz_question_count(completed_quiz_id)
        question_indices = common.get_quiz_question_indices(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    if question_count == 20:
        return fl.redirect(fl.url_for("quiz._done", _method="GET", completed_quiz_id=completed_quiz_id))

    return fl.render_template(
        "quiz/form.html",
        creator_name=creator_name,
        friend_name=friend_name,
        question_count=question_count,
        question=static.G_QUESTIONS[question_indices[current_question_index]],
        question_index=question_indices[current_question_index],
        completed_quiz_id=completed_quiz_id
    )


@g_blueprint.route("/form/<completed_quiz_id>/skip", methods=("POST",))
def _form_skip(completed_quiz_id):
    try:
        common.next_completed_quiz_question(completed_quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))

    return fl.redirect(fl.url_for("quiz._form", _method="GET", completed_quiz_id=completed_quiz_id))


@g_blueprint.route("/done/<completed_quiz_id>")
def _done(completed_quiz_id):
    # TODO display the results
    return fl.render_template("quiz/done.html")
