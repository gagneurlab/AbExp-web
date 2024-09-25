# AbExp web interface

This is the web interface for the [AbExp](https://github.com/gagneurlab/abexp) project.
It is a simple web interface that allows users to get the AbExp scores for precomputed variants.
The web interface is built using the Flask web framework.

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

To set the environment variables, creae a `.env` file in the root of the project.
You can simply copy `.env.development` and rename it to `.env`.

```bash

To set up duckdb:
    
```bash
poetry run flask init-db
```

To run the web app, run:

```bash
poetry run flask run
```

