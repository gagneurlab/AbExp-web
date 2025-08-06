import duckdb
from flask import g, current_app
import click
from pathlib import Path

ABEXP_PQ_NAME = 'abexp.parquet'
GENE_MAP_TSV_NAME = 'gene_map.tsv'
TISSUES_TXT_NAME = 'tissues.txt'
GENOMES_TXT_NAME = 'genomes.txt'


def get_db():
    db_p = current_app.config['DB_PATH']
    if 'db' not in g:
        g.db = duckdb.connect(db_p)

    return g.db


def init_db():
    db = get_db()
    dataset_path = Path(current_app.config['DATA_PATH']) / ABEXP_PQ_NAME / '**/*.parquet'
    gene_map_path = Path(current_app.config['DATA_PATH']) / GENE_MAP_TSV_NAME
    genomes_path = Path(current_app.config['DATA_PATH']) / GENOMES_TXT_NAME
    tissues_path = Path(current_app.config['DATA_PATH']) / TISSUES_TXT_NAME
    score_column = current_app.config['SCORE_COLUMN']

    click.echo('Creating abexp view...')

    db.execute(f"""
    CREATE OR REPLACE VIEW abexp AS 
    SELECT genome, concat_ws(':', chrom, (start + 1), "ref" || '>' || "alt") AS 'variant', chrom, 
        start, "end", ref, alt, gene, tissue, tissue_type,"{score_column}" AS 'abexp_score'
    FROM read_parquet('{dataset_path}', hive_partitioning = True);
    """)

    click.echo('Creating gene map...')

    db.execute(f"""
    CREATE OR REPLACE TABLE gene_map AS
    SELECT gene_id as gene, group_concat(gene_name, ', ') as gene_name
    FROM read_csv('{gene_map_path}', header = True, sep = "\t")
    GROUP BY gene_id; 
    """)

    click.echo('Creating genomes table...')

    db.execute(f"""
    CREATE OR REPLACE TABLE genomes AS
    SELECT column0 as genome FROM read_csv('{genomes_path}', header = False, sep = "\n")
    WHERE column0 IS NOT NULL AND column0 != '';
    """)

    click.echo('Creating tissues table...')

    db.execute(f"""
    CREATE OR REPLACE TABLE tissues AS
    SELECT column0 as tissue FROM read_csv('{tissues_path}', header = False, sep = "\n")
    WHERE column0 IS NOT NULL AND column0 != '';
    """)


@click.command('init-db')
def init_db_command():
    click.echo('Initializing the database...')
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.cli.add_command(init_db_command)
    app.teardown_appcontext(close_db)
