import os
import sys

import flask as fl

from . import question
from . import glob

# https://flask.palletsprojects.com/en/stable/tutorial/views/
# https://sqlite.org/lang.html


def create_app():
    application = fl.Flask(__name__, instance_relative_config=True)
    application.config.from_mapping(
        SECRET_KEY="dev",  # Will be overriden
        DATABASE=os.path.join(application.instance_path, "bs-free-friendship-test.sqlite")
    )

    # Apply some more configuration from the file
    try:
        application.config.from_pyfile("configuration.py")
    except Exception as err:
        print(f"Error configuration file: {err}", file=sys.stderr)

    _initialize_application(application)

    # Ensure the instance directory is available
    os.makedirs(application.instance_path, exist_ok=True)

    with application.open_resource("questions.json") as file:
        glob.QUESTIONS = question.load_questions(file)

    @application.route("/hello")
    def hello():
        return "Hello, world!"

    return application


def _initialize_application(application: fl.Flask):
    from . import database
    from . import commands
    from . import create
    from . import test

    application.teardown_appcontext(database.close_database)
    application.cli.add_command(commands.command_initialize_database)
    application.register_blueprint(create.g_blueprint)
    application.register_blueprint(test.g_blueprint)
