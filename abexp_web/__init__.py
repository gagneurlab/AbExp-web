from flask import Flask, render_template, request, flash, redirect, url_for
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from . import utils
from .constants import BINARY_MAP, CSP
from . import abexp as abexp_service
from .config import Config
from . import db
from markupsafe import escape


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # load the configuration from the config file
    app.config.from_pyfile(f'config/{app.config["FLASK_ENV"]}.cfg')

    # Enable Content Security Policy (CSP)
    Talisman(app, content_security_policy=CSP, force_https=app.config['FORCE_HTTPS'])

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
        # Get the user's input from the form
        snv_input = utils.parse_input(escape(request.form['snv_input']))
        max_score_only = BINARY_MAP[request.form['max_score']]
        tissues = request.form.getlist('tissue_checkbox')
        extra_info = BINARY_MAP[request.form['extra_info']]
        try:
            df = abexp_service.run_abexp(snv_input, max_score_only, tissues, extra_info)
            return render_template('result.html', output=df.tolist(),
                                   unique_column1_values=sorted(set(df['variant'].unique().values())),
                                   unique_column2_values=sorted(set(df['gene_id'].unique().values())),
                                   unique_column4_values=sorted(set(df['tissue'].unique().values())),
                                   csv_output=df.to_csv(index=False))
        except Exception as e:
            error_message = str(e)
            flash(error_message, 'error')
            return redirect(url_for('index'))

    db.init_app(app)

    return app
