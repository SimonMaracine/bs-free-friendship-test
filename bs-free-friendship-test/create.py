import flask as fl

def create_blueprint() -> fl.Blueprint:
    return fl.Blueprint("create", __name__, url_prefix="/create")
