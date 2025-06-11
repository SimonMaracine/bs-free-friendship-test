import click

from . import database


@click.command("initialize-database")
def command_initialize_database():
    database.initialize_database()
    click.echo("Recreated the database")


@click.command("show-database")
def command_show_database():
    database.show_database()
    click.echo("Showed the database")
