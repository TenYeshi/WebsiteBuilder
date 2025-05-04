import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from forms import WelcomeMessageForm, ApplicationForm, ApplicationFeedbackForm

# Import our OpenAI helper functions
from utils.openai_helper import generate_welcome_message

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__, 
            static_folder='web/static',
            template_folder='web/templates')
app.secret_key = os.environ.get("SESSION_SECRET", "tenyeshi-portfolio-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Import models after defining db
from models import Project, Message, Application

# Create tables within application context
with app.app_context():
    db.create_all()

    # Add sample projects if none exist
    if Project.query.count() == 0:
        sample_projects = [
            Project(
                title='Portfolio Website',
                description='A responsive portfolio website built with Flask and Bootstrap.',
                image_url='/static/img/logo.png'
            ),
            Project(
                title='E-commerce Platform',
                description='A full-featured online store with product listings and shopping cart.',
                image_url='/static/img/logo2.png'
            ),
            Project(
                title='Mobile App Design',
                description='UI/UX design for a fitness tracking mobile application.',
                image_url='/static/img/logo3.png'
            )
        ]
        db.session.add_all(sample_projects)
        db.session.commit()

# Home route
@app.route('/')
def home():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

# Static page routes
@app.route('/index.html')
def home_page():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', 'No Subject')
        message_text = request.form.get('message')
        
        if name and email and message_text:
            # Create new message in the database
            new_message = Message(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            db.session.add(new_message)
            db.session.commit()
            
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all required fields', 'danger')
    
    return render_template('contact.html')

# Welcome Message Generator
@app.route('/welcome-message', methods=['GET', 'POST'])
def welcome_message():
    form = WelcomeMessageForm()
    welcome_text = None
    api_error = None
    
    if form.validate_on_submit():
        # Gather visitor information
        visitor_info = {
            'name': form.name.data or 'there',
            'time_of_day': form.time_of_day.data or 'today',
            'location': form.location.data or ''
        }
        
        try:
            # Generate personalized welcome message
            welcome_text = generate_welcome_message(visitor_info)
            
            # Check if we're using the API key
            if not os.environ.get('OPENAI_API_KEY'):
                api_error = "OpenAI API key is not configured. Using fallback messaging."
                
        except Exception as e:
            app.logger.error(f"Error in welcome message generation: {e}")
            welcome_text = generate_welcome_message(visitor_info)  # This will use fallback
            api_error = "There was an issue with the OpenAI API. Using fallback message generation."
        
    return render_template('welcome_message.html', form=form, welcome_text=welcome_text, api_error=api_error)

# AJAX endpoint for welcome message generation
@app.route('/api/generate-welcome', methods=['POST'])
def api_generate_welcome():
    data = request.json
    visitor_info = {
        'name': data.get('name', 'there'),
        'time_of_day': data.get('time_of_day', 'today'),
        'location': data.get('location', '')
    }
    
    try:
        welcome_text = generate_welcome_message(visitor_info)
        
        # Check if API key is missing
        if not os.environ.get('OPENAI_API_KEY'):
            return jsonify({
                'status': 'partial_success',
                'message': welcome_text,
                'note': "OpenAI API key is not configured. Using fallback messaging."
            })
            
        return jsonify({'status': 'success', 'message': welcome_text})
    except Exception as e:
        app.logger.error(f"API welcome message error: {e}")
        # Still generate a fallback message
        fallback_text = generate_welcome_message(visitor_info)  # Will use fallback
        return jsonify({
            'status': 'error', 
            'message': fallback_text,
            'error': str(e)
        })

# Word Processor Application
@app.route('/word-processor')
def word_processor():
    return render_template('word_processor/index.html')

# Application submission routes
@app.route('/submit-application', methods=['GET', 'POST'])
def submit_application():
    form = ApplicationForm()
    
    if form.validate_on_submit():
        # Create new application
        new_application = Application(
            applicant_name=form.applicant_name.data,
            email=form.email.data,
            application_type=form.application_type.data,
            content=form.content.data,
            status='pending'
        )
        db.session.add(new_application)
        db.session.commit()
        
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('submit_application.html', form=form)

# Dashboard for application management
@app.route('/dashboard')
def dashboard():
    applications = Application.query.order_by(Application.created_at.desc()).all()
    return render_template('dashboard.html', applications=applications)

# View a single application
@app.route('/application/<int:application_id>')
def view_application(application_id):
    application = Application.query.get_or_404(application_id)
    return render_template('view_application.html', application=application)

# Update application status (approve or reject)
@app.route('/application/<int:application_id>/update-status', methods=['POST'])
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    new_status = request.form.get('status')
    
    if new_status in ['approved', 'rejected']:
        application.status = new_status
        application.feedback = request.form.get('feedback', '')
        application.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Application has been {new_status}!', 'success')
    
    return redirect(url_for('dashboard'))

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404