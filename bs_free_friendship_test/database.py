import sqlite3

import flask as fl


class DatabaseError(Exception):
    def __init__(self, error_code: int | None, *args: object):
        super().__init__(*args)
        self.error_code = error_code


def open_database_ex(application: fl.Flask) -> sqlite3.Connection:
    return _create_connection(application.config["DATABASE"])


def open_database() -> sqlite3.Connection:
    # Stupid syntax
    if "database" not in fl.g:
        fl.g.database = open_database_ex(fl.current_app)

    return fl.g.database


def close_database(_=None):
    database = fl.g.pop("database", None)

    if database is not None:
        database.close()


def initialize_database(application: fl.Flask):
    with open_database_ex(application) as db:
        with fl.current_app.open_resource("schema.sql") as file:
            try:
                db.executescript(file.read().decode("utf8"))
            except db.Error as err:
                raise DatabaseError(err.sqlite_errorcode, f"Could not execute script: {err}")
            except Exception as err:
                raise DatabaseError(None, f"Could not execute script: {err}")


def _create_connection(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row

    return connection
