import click

from . import database


@click.command("initialize-database")
def command_initialize_database():
    database.initialize_database()
    click.echo("Recreated the database")
