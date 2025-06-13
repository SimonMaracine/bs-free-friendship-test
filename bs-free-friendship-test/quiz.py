import flask as fl


g_blueprint = fl.Blueprint("quiz", __name__, url_prefix="/quiz")


@g_blueprint.route("/form", methods=("GET", "POST"))
def _form():
    if fl.request.method == "POST":
        print("post")

    return fl.render_template("quiz/form.html")
