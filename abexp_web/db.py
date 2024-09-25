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
    dataset_path = current_app.config['DATASET_PATH']
    score_column = current_app.config['SCORE_COLUMN']
    gene_map_path = current_app.config['GENE_MAP_PATH']

    db.execute(f"""
    CREATE OR REPLACE VIEW abexp AS 
    SELECT genome, concat_ws(':', chrom, (start + 1), "ref" || '>' || "alt") AS 'variant', chrom, 
        start, "end", ref, alt, gene, tissue, tissue_type,"{score_column}" AS 'abexp_score'
    FROM '{dataset_path}';
    """)

    db.execute("""
    CREATE OR REPLACE TABLE tissue_types AS
    SELECT DISTINCT tissue_type FROM abexp ORDER BY tissue_type;
    """)

    db.execute("""
    CREATE OR REPLACE TABLE tissues AS
    SELECT DISTINCT tissue FROM abexp ORDER BY tissue;
    """)

    db.execute("""
    CREATE OR REPLACE TABLE genomes AS
    SELECT DISTINCT genome FROM abexp ORDER BY genome;
    """)

    db.execute(f"""
    CREATE OR REPLACE TABLE gene_map AS
    SELECT gene_id as gene, group_concat(gene_name, ', ') as gene_name
    FROM read_csv('{gene_map_path}', header = True, sep = "\t")
    GROUP BY gene_id; 
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
