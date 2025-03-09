import flask as fl

g_blueprint = fl.Blueprint("create", __name__, url_prefix="/create")


@g_blueprint.route("/start", methods=("GET", "POST"))
def _start():
    if fl.request.method == "POST":
        print("post")

    return fl.render_template("create/start.html")
