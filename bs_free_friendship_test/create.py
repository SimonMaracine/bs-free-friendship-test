import flask as fl

from . import database
from . import static
from . import common


g_blueprint = fl.Blueprint("create", __name__, url_prefix="/create")


@g_blueprint.route("/start", methods=("GET", "POST"))
def _start():
    if fl.request.method == "POST":
        creator_name = fl.request.form["creator_name"]

        if not common.valid_name(creator_name):
            fl.flash("Invalid name")
        else:
            try:
                quiz_id = common.create_new_quiz(creator_name.strip())
            except database.DatabaseError as err:
                fl.flash(str(err))
            else:
                return fl.redirect(fl.url_for("create._form", _method="GET", quiz_id=quiz_id))

    return fl.render_template("create/start.html")


@g_blueprint.route("/form/<quiz_id>", methods=("GET", "POST"))
def _form(quiz_id):
    if fl.request.method == "POST":
        print(fl.request.form)

        question_index, answers = common.get_form_answers(fl.request.form)

        if not answers:
            fl.flash("You must either submit an answer or skip the question")
        else:
            try:
                common.add_quiz_question_answer(quiz_id, question_index, answers)
                common.next_quiz_question(quiz_id)
            except database.DatabaseError as err:
                fl.flash(str(err))

    try:
        creator_name, shuffled_question_indices, current_question_index = common.get_quiz_data(quiz_id)
        question_count = common.get_quiz_question_count(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start", _method="GET"))

    if question_count == 20:
        return fl.redirect(fl.url_for("create._done", _method="GET", quiz_id=quiz_id))

    return fl.render_template(
        "create/form.html",
        creator_name=creator_name,
        question_count=question_count,
        question=static.G_QUESTIONS[shuffled_question_indices[current_question_index]],
        question_index=shuffled_question_indices[current_question_index],
        quiz_id=quiz_id
    )


@g_blueprint.route("/form/<quiz_id>/skip", methods=("POST",))
def _form_skip(quiz_id):
    try:
        common.next_quiz_question(quiz_id)
    except database.DatabaseError as err:
        fl.flash(str(err))

    return fl.redirect(fl.url_for("create._form", _method="GET", quiz_id=quiz_id))


@g_blueprint.route("/done/<quiz_id>")
def _done(quiz_id):
    results: list[tuple[str, int]] = []

    try:
        creator_name, _, _ = common.get_quiz_data(quiz_id)
        quiz_completed_quizes = common.get_quiz_completed_quizes(quiz_id)

        for quiz in quiz_completed_quizes:
            quiz_score = common.get_quiz_score(quiz[0])
            results.append((quiz[1], int(quiz_score)))
    except database.DatabaseError as err:
        fl.flash(str(err))
        return fl.redirect(fl.url_for("create._start"))

    return fl.render_template("create/done.html", creator_name=creator_name, quiz_id=quiz_id, results=results)
