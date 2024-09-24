import duckdb
from flask import g, current_app
import click


def get_db():
    db_p = current_app.config['DB_PATH']
    if 'db' not in g:
        g.db = duckdb.connect(db_p)

    return g.db


def init_db():
    db = get_db()
    dataset_p = current_app.config['DATASET_PATH']
    db.execute(f"""
    CREATE OR REPLACE VIEW abexp_veff AS SELECT * FROM '{dataset_p}';
    """)


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.cli.add_command(init_db_command)
    app.teardown_appcontext(close_db)
