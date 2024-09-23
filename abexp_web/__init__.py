from flask import Flask, render_template, request
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .utils import parse_input
from .constants import BINARY_MAP
from . import abexp as abexp_service
from .config import Config
from markupsafe import escape

csp = {
    'default-src': [
        "'self'",
        "https://stackpath.bootstrapcdn.com",
        "https://code.jquery.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "https://cdn.datatables.net"
    ],
    'img-src': [
        "'self'",
        "data:",
        "https://stackpath.bootstrapcdn.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.datatables.net"
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        "https://stackpath.bootstrapcdn.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.datatables.net"
    ],
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        "https://code.jquery.com",
        "https://cdn.jsdelivr.net",
        "https://stackpath.bootstrapcdn.com",
        "https://cdn.datatables.net"
    ],
    'font-src': [
        "'self'",
        "https://cdnjs.cloudflare.com"
    ]
}


def create_app():
    app = Flask(__name__)

    # load the configuration from the config file
    app.config.from_object(Config)
    print(app.config)
    print(app.config['FORCE_HTTPS'])
    app.config.from_pyfile(f'config/{app.config["FLASK_ENV"]}.cfg')

    # Enable Content Security Policy (CSP)
    Talisman(app, content_security_policy=csp, force_https=app.config['FORCE_HTTPS'])

    Limiter(
        get_remote_address,
        app=app,
        default_limits=["300 per day", "60 per hour"],
    )

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/run_abexp', methods=['POST'])
    def run_abexp():
        snv_input = parse_input(escape(request.form['snv_input']))
        genome = request.form['genome']
        max_score_only = BINARY_MAP[request.form['max_score']]
        tissues = request.form.getlist('tissue_checkbox')
        extra_info = BINARY_MAP[request.form['extra_info']]
        abexp_service.run_abexp(snv_input, genome, max_score_only, tissues, extra_info)

    return app
