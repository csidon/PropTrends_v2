# Creating HTML forms with classes from flask_wtf

from flask_wtf import FlaskForm				# Provides form validation functionality
from flask_wtf.file import FileField, FileAllowed	# Provides ability for the form to manage files/images
from flask_login import current_user				
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from proptrends.models import User

class RegistrationForm(FlaskForm):
	user_first_name = StringField('First Name', validators=[DataRequired()])
	user_last_name = StringField('Last Name', validators=[DataRequired()])
	user_email = StringField('Email (This will also be your username)', validators=[DataRequired(), Email()])
	user_password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
	confirm_password = PasswordField('Confirm your password', validators=[DataRequired(), EqualTo('user_password', message='Password must match')])
	submit = SubmitField('Create account')

	def validate_user_email(self, user_email):
		user = User.query.filter_by(user_email=user_email.data).first()
		# If the user query is none, nothing happens. Otherwise if the query returns data, throw validation error message
		if user:
			raise ValidationError("That email already exists. Please register with another email address")


class LoginForm(FlaskForm):
	user_email = StringField('Email address', validators=[DataRequired(), Email()])
	user_password = PasswordField('Password', validators=[DataRequired()])

	# Remembers user's information so that they do not need to re-login if they close their browser
	# using a secure cookie
	user_remember = BooleanField('Remember Me')

	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	user_first_name = StringField('First Name', validators=[DataRequired()])
	user_last_name = StringField('Last Name', validators=[DataRequired()])
	user_email = StringField('Email (This will also be your username)', validators=[DataRequired(), Email()])
	user_image = FileField('Update your profile picture', validators=[FileAllowed(['jpg', 'png'])])
	upload_image = FileField('Update your profile picture', validators=[FileAllowed(['jpg', 'png'])])

	submit = SubmitField('Update')

	def validate_user_email(self, user_email):
		if user_email.data != current_user.user_email:
			user = User.query.filter_by(user_email=user_email.data).first()
			# If the user query is none, nothing happens. Otherwise if the query returns data, throw validation error message
			if user:
				raise ValidationError("That email already exists. Please register with another email address")