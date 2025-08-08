import duckdb
from flask import g, current_app
import click
from pathlib import Path
from tqdm import tqdm

ABEXP_PQ_NAME = 'abexp.parquet'
GENE_MAP_TSV_NAME = 'gene_map.tsv'
TISSUES_TXT_NAME = 'tissues.txt'
GENOMES_TXT_NAME = 'genomes.txt'
CHROMOSOMES_TXT_NAME = 'chromosomes.txt'


def get_db(read_only=True):
    if not read_only:
        Path(current_app.config['DB_PATH']).mkdir(parents=True, exist_ok=True)
    db_p = Path(current_app.config['DB_PATH']) / 'abexp.duckdb'
    if 'db' not in g:
        g.db = duckdb.connect(db_p, read_only=read_only)

    return g.db


def create_gene_map_table(db, gene_map_path):
    """Create the gene map table from TSV file."""
    click.echo('Creating gene map...')
    db.execute(f"""
    CREATE  TABLE IF NOT EXISTS gene_map AS
    SELECT gene_id as gene, group_concat(gene_name, ', ') as gene_name
    FROM read_csv('{gene_map_path}', header = True, sep = "\t")
    GROUP BY gene_id; 
    """)


def create_enum_types(db, genomes_path, tissues_path, chromosomes_path):
    """Create enum types for genome, tissue, and chromosome."""

    existing_types = db.execute("""SELECT type_name FROM duckdb_types WHERE logical_type = 'ENUM';""").fetchall()
    existing_types = [t[0] for t in existing_types]

    click.echo('Creating genome enum...')
    if 'genome' not in existing_types:
        db.execute(f"""
            CREATE TYPE genome AS ENUM (
                SELECT column0 as genome FROM read_csv('{genomes_path}', header = False, sep = "\n")
                WHERE column0 IS NOT NULL AND column0 != ''
            );
        """)
    else:
        click.echo('Genome enum already exists, skipping creation.')
        

    click.echo('Creating tissue enum...')
    if 'tissue' not in existing_types:
        db.execute(f"""
            CREATE TYPE tissue AS ENUM (
                SELECT column0 as tissue FROM read_csv('{tissues_path}', header = False, sep = "\n")
                WHERE column0 IS NOT NULL AND column0 != ''
            );
        """)
    else:
        click.echo('Tissue enum already exists, skipping creation.')

    click.echo('Creating chromosome enum...')
    if 'chromosome' not in existing_types:
        db.execute(f"""
            CREATE TYPE chromosome AS ENUM (
                SELECT column0 as chromosome FROM read_csv('{chromosomes_path}', header = False, sep = "\n")
                WHERE column0 IS NOT NULL AND column0 != ''
            );
        """)
    else:
        click.echo('Chromosome enum already exists, skipping creation.')

def create_abexp_table(db, dataset_base_path, score_column):
    """Load data from parquet files into the abexp table."""
    click.echo('Loading Hive-partitioned parquet dataset...')
    
    # Configure DuckDB for memory-efficient processing
    
    db.execute(f"""
    CREATE VIEW IF NOT EXISTS abexp AS 
    SELECT genome, chrom, start, "end", ref, alt, gene, tissue, "{score_column}" AS 'abexp_score'
    FROM read_parquet('{dataset_base_path / '**/*.parquet'}', hive_partitioning = True);
    """)
    
    click.echo('Finished inserting data into abexp table')

def init_db(memory_limit='2GB', threads=4):
    """Initialize the database with all tables and data."""
    db = get_db(read_only=False)
    dataset_base_path = Path(current_app.config['DATA_PATH']) / ABEXP_PQ_NAME
    gene_map_path = Path(current_app.config['DATA_PATH']) / GENE_MAP_TSV_NAME
    genomes_path = Path(current_app.config['DATA_PATH']) / GENOMES_TXT_NAME
    tissues_path = Path(current_app.config['DATA_PATH']) / TISSUES_TXT_NAME
    chromosomes_path = Path(current_app.config['DATA_PATH']) / CHROMOSOMES_TXT_NAME
    score_column = current_app.config['SCORE_COLUMN']

    # Create all database components
    create_gene_map_table(db, gene_map_path)
    create_enum_types(db, genomes_path, tissues_path, chromosomes_path)
    create_abexp_table(db, dataset_base_path, score_column)

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
