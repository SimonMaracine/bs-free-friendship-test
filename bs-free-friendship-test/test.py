import flask as fl


g_blueprint = fl.Blueprint("test", __name__, url_prefix="/test")


@g_blueprint.route("/form", methods=("GET", "POST"))
def _form():
    if fl.request.method == "POST":
        print("post")

    return fl.render_template("test/form.html")
