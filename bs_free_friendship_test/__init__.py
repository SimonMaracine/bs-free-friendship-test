import os
import atexit

import flask as fl
import apscheduler.schedulers.background
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    from . import question
    from . import static

    application = fl.Flask(__name__, instance_relative_config=True)
    application.config.from_mapping(
        SECRET_KEY="dev",  # Gets overriden by configuration
        DATABASE=os.path.join(application.instance_path, "bs-free-friendship-test.sqlite")
    )

    # Apply some more configuration from the file
    if application.config.from_pyfile("configuration.py", True):
        application.logger.info("Using configuration file")

    _initialize_application(application)
    _setup_delete_scheduler(application)  # In debug mode, this will run twice

    # Ensure the instance directory is available
    os.makedirs(application.instance_path, exist_ok=True)

    with application.open_resource("questions.json") as file:
        static.G_QUESTIONS = question.load_questions(file)

    application.logger.info(f"Questions: {len(static.G_QUESTIONS)}")

    @application.route("/")
    def index():
        return fl.render_template("index.html")

    @application.route("/information")
    def information():
        return fl.render_template("information.html")

    application.wsgi_app = ProxyFix(application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    return application


def _initialize_application(application: fl.Flask):
    from . import database
    from . import commands
    from . import create
    from . import quiz

    application.teardown_appcontext(database.close_database)
    application.cli.add_command(commands.command_initialize_database)
    application.register_blueprint(create.g_blueprint)
    application.register_blueprint(quiz.g_blueprint)


def _setup_delete_scheduler(application: fl.Flask):
    scheduler = apscheduler.schedulers.background.BackgroundScheduler()
    scheduler.add_job(lambda: _delete_old_quizes(application), trigger="interval", seconds=1800)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


def _delete_old_quizes(application: fl.Flask):
    from . import database
    from . import common

    with database.open_database_ex(application) as db:
        try:
            common.delete_quizes_older_than(db, 48)
        except database.DatabaseError as err:
            application.logger.error(f"Error deleting quizes: {err}")
