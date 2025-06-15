import sys

import flask as fl
import click

from . import database


@click.command("initialize-database")
def command_initialize_database():
    try:
        database.initialize_database(fl.current_app)
    except database.DatabaseError as err:
        print(err, file=sys.stderr)
