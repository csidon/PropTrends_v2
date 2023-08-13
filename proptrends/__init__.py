from flask import Flask
from flask_sqlalchemy import SQLAlchemy	# Manages database sync
from flask_bcrypt import Bcrypt			# Hashes passwords so that they are secure
from flask_login import LoginManager	# Manages logins/cookies

application = Flask(__name__)

# # Set a secret key to prevent against modifying cookies and XSS requests on forms (randomly generated using python's secrets.token_hex)
application.config['SECRET_KEY'] = 'ea3c9fdee984c581c3272cb37b6268746bc67adcdbb60ede'
# format for the URI is postgresql://{user}:{passwosrd}@{RDS endpoint}/{db name, default is postgres}
# application.config['SQLALCHEMY_DATABASE_URI'] = \
#     'i.e. postgresql://postgresmaster:1NewPass!@s3-lambda-rdspostgresv2.clbvaq8mp9jk.us-east-1.rds.amazonaws.com:5432/default'    # For future RDS

application.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1NewPass!@localhost:5432/postgres' # My local db
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)
application.app_context().push()

bcrypt = Bcrypt(application)
loginManager = LoginManager(application)
loginManager.login_view = 'users.login'			# Flask function that brings user back to login page if they haven't logged in
loginManager.login_message_category = 'info'		# Makes pretty - Assigns Bootstraps' "info" category styling to login-related messages

from proptrends.models import *
from proptrends.users.routes import users
# from boostly.clients.routes import clients
from proptrends.main.routes import main
from proptrends.scraper import routes
from proptrends.scraper.routes import *
from proptrends.scraper.routes import scraper
# from boostly.alerts.routes import alerts
# from proptrends.scraper import main
#
application.register_blueprint(users)
# application.register_blueprint(clients)
application.register_blueprint(main)
# application.register_blueprint(alerts)
application.register_blueprint(scraper)
from proptrends.main.utils import format_currency, format_area2
application.jinja_env.filters['currency'] = format_currency
application.jinja_env.filters['area2'] = format_area2
