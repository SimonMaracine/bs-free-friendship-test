import flask as fl

def create_blueprint() -> fl.Blueprint:
    return fl.Blueprint("test", __name__, url_prefix="/test")
