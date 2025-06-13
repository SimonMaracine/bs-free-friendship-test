import sys

import click

from . import database


@click.command("initialize-database")
def command_initialize_database():
    try:
        database.initialize_database()
    except database.DatabaseError as err:
        print(err, file=sys.stderr)
