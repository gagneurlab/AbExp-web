# AbExp web interface

This is the web interface for the [AbExp](https://github.com/gagneurlab/abexp) project, based on the [AbSplice-web-interface](https://github.com/neverov-am/absplice_web_interface). It is a simple web interface that allows users to get the AbExp scores for precomputed variants.
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

## Deployment
To deploy the app in production, define a .env file with the following variables.
Make sure to define the SECRET_KEY variable to something random. 
The production environment will only with https.

```bash
FLASK_ENV=production
SECRET_KEY=<secret_key>
DATA_PATH = './data'
ABEXP_SCORE_COLUMN = 'abexp_v1.1'
```

To deploy the app, run:

```bash
docker compose up -d
```



