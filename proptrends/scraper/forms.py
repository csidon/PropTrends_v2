from flask_wtf import FlaskForm				# Provides form validation functionality			
from wtforms import SubmitField, SelectField

from wtforms.validators import DataRequired

class ScrapeSuburbForm(FlaskForm):
    suburb_to_scrape = SelectField(u'Region to scrape', choices=[('Wellington','Wellington'), ('Auckland', 'Auckland, Not available at the moment.. Coming Soon!')], validators=[DataRequired()])
    # On expansion to include multiple Regions, Districts, and Suburbs, this would be moved to a table allowing dynamic select.
    submit = SubmitField('Run Scraper')