from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, URL, Optional

class LoginForm(FlaskForm):
    username = StringField('Application ID or Roll Number', validators=[DataRequired()])
    password = PasswordField('Email Address', validators=[DataRequired()])
    remember = BooleanField('Remember My Details')
    submit = SubmitField('Check Status')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send Message')

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Add Project')

class ApplicationForm(FlaskForm):
    applicant_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    father_name = StringField('Father\'s Name', validators=[Length(min=2, max=100)])
    roll_number = StringField('Roll Number', validators=[Length(max=20)])
    class_name = StringField('Class', validators=[Length(max=50)])
    date_of_birth = StringField('Date of Birth (YYYY-MM-DD)', validators=[Optional(), Length(max=10)])
    address = TextAreaField('Address', validators=[Length(max=200)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    content = TextAreaField('Additional Comments', validators=[Length(min=0, max=500)])
    submit = SubmitField('APPLY NOW')

class ApplicationFeedbackForm(FlaskForm):
    feedback = TextAreaField('Feedback', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Submit Feedback')

class ApplicationSearchForm(FlaskForm):
    search_query = StringField('Search by Name or Roll Number', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Search')

class WelcomeMessageForm(FlaskForm):
    name = StringField('Your Name', validators=[Optional(), Length(max=64)], 
                      description="Enter your name for a personalized greeting")
    time_of_day = SelectField('Time of Day', 
                             choices=[('morning', 'Morning'), 
                                     ('afternoon', 'Afternoon'), 
                                     ('evening', 'Evening'),
                                     ('night', 'Night')],
                             validators=[Optional()],
                             description="Select the time of day")
    location = StringField('Your Location', validators=[Optional(), Length(max=100)],
                          description="Enter your city or country (optional)")
    submit = SubmitField('Generate Welcome Message')
