import flask as fl

from . import database
from . import static
from . import common


g_blueprint = fl.Blueprint("quiz", __name__, url_prefix="/quiz")


@g_blueprint.route("/start/<public_quiz_id>", methods=("GET", "POST"))
def _start(public_quiz_id):
    if fl.request.method == "POST":
        friend_name = fl.request.form["friend_name"]

        try:
            quiz_id = common.get_quiz_id_from_public_id(public_quiz_id)
        except database.DatabaseError as err:
            fl.flash(str(err))
            return common.redirect_to_create_start(fl)

        try:
            completed_quiz_id = common.create_new_completed_quiz(friend_name, quiz_id)
        except database.DatabaseError as err:
            fl.flash(str(err))
        else:
            return fl.redirect(fl.url_for("quiz._form", _method="GET", completed_quiz_id=completed_quiz_id))

    try:
        quiz_id = common.get_quiz_id_from_public_id(public_quiz_id)
        question_count = common.get_quiz_question_count(quiz_id)
        _, creator_name, _, _ = common.get_quiz_data(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return common.redirect_to_create_start(fl)

    if question_count < 20:
        fl.flash("Quiz is not ready")
        return common.redirect_to_create_start(fl)

    return fl.render_template("quiz/start.html", creator_name=creator_name)


@g_blueprint.route("/form/<completed_quiz_id>", methods=("GET", "POST"))
def _form(completed_quiz_id):
    if fl.request.method == "POST":
        question_index, answers = common.get_form_answers(fl.request.form)

        if not answers:
            fl.flash("You must either submit an answer or skip the question")
        else:
            try:
                common.add_completed_quiz_question_answer(completed_quiz_id, question_index, answers)
            except database.DatabaseError as err:
                fl.flash(str(err))

            try:
                common.next_completed_quiz_question(completed_quiz_id)
            except database.DatabaseError as err:
                fl.flash(str(err))
                return common.redirect_to_create_start(fl)

    try:
        friend_name, current_question_index, quiz_id = common.get_completed_quiz_data(completed_quiz_id)
        question_count = common.get_completed_quiz_question_count(completed_quiz_id)
        question_indices = common.get_quiz_question_answer_indices(quiz_id)
        _, creator_name, _, _ = common.get_quiz_data(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return common.redirect_to_create_start(fl)

    assert question_count <= 20

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
        return common.redirect_to_create_start(fl)

    return fl.redirect(fl.url_for("quiz._form", _method="GET", completed_quiz_id=completed_quiz_id))


@g_blueprint.route("/done/<completed_quiz_id>")
def _done(completed_quiz_id):
    try:
        friend_name, _, quiz_id = common.get_completed_quiz_data(completed_quiz_id)
        quiz_score = common.get_quiz_score(completed_quiz_id)
        _, creator_name, _, _ = common.get_quiz_data(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return common.redirect_to_create_start(fl)

    return fl.render_template("quiz/done.html", creator_name=creator_name, friend_name=friend_name, quiz_score=int(quiz_score))
