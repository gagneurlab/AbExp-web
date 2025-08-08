"""Flask config."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Set Flask config variables."""
    FLASK_ENV = environ.get('FLASK_ENV', 'production')
    SECRET_KEY = environ.get('SECRET_KEY')
    FORCE_HTTPS = environ.get('FORCE_HTTPS', False)
    DATA_PATH = environ.get('DATA_PATH', None)
    SCORE_COLUMN = environ.get('ABEXP_SCORE_COLUMN', 'abexp_v1.1')
    DB_PATH = environ.get('ABEXP_DB_PATH', 'duckdb')
    TESTING = False
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
