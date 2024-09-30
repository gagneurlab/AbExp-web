# AbExp web interface

This is the web interface for the [AbExp](https://github.com/gagneurlab/abexp) project, based on the [AbSplice-web-interface](https://absplice.cmm.cit.tum.de/). It is a simple web interface that allows users to get the AbExp scores for precomputed variants.
The web interface is built using the Flask web framework.

## Dataset

The app requires the following files to run. Test files can be found in the **example_files** directory.

- A parquet file containing the precomputed AbExp scores for various genome-gene-variant-tissue combinations. The file may be partitioned.
    - File name: **abexp.parquet**:
    - Columns:
        - genome
        - chrom
        - start # (0-based)
        - end # (1-based)
        - ref
        - alt
        - gene
        - tissue
        - tissue_type
        - <score_column> # The default is *abexp_v1.1*, but may be modified by setting the environment variable *ABEXP_SCORE_COLUMN*.
- A TSV file containing the gene map of the Ensembl gene-IDs to their corresponding gene-names.
    - File name: **gene_map.tsv**
    - Columns:
        - gene_id
        - gene_name

## Development

The project is packaged using poetry.

To install poetry, run:

```bash
pipx install poetry
```

To install the web app, run:

```bash
poetry install
# to install the development dependencies
#poetry install --with dev
```

To set the environment variables, create a `.env` file in the root of the project.
You can simply copy `.env.development` and rename it to `.env`.

To set up duckdb:
    
```bash
poetry run flask init-db
```

To run the web app, run:

```bash
poetry run flask run
```

## Deployment
To deploy the app in production, define a .env file with the following variables.
Make sure to define the SECRET_KEY variable to something random. 
The production environment will redirect all requests to https.

```bash
FLASK_ENV=production
SECRET_KEY=<secret_key> # should be something random
DATA_PATH='./data' # the location of the dataset, as defined above
ABEXP_SCORE_COLUMN='abexp_v1.1' # the column name of the abexp-score in the abexp.parquet file
```

To deploy the app, run:

```bash
docker compose up -d
```



