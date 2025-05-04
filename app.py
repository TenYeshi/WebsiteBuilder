import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from forms import WelcomeMessageForm, ApplicationForm, ApplicationFeedbackForm, LoginForm, ApplicationSearchForm

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
    existing_applications = None
    
    # Handle search query
    search_query = request.args.get('search_query', '')
    if search_query:
        # Search for existing applications by name or roll number
        existing_applications = Application.query.filter(
            db.or_(
                Application.applicant_name.ilike(f'%{search_query}%'),
                Application.roll_number.ilike(f'%{search_query}%')
            )
        ).order_by(Application.created_at.desc()).all()
    
    # Handle prefill from existing application
    prefill_id = request.args.get('prefill')
    if prefill_id and request.method == 'GET':
        try:
            prefill_app = Application.query.get(int(prefill_id))
            if prefill_app:
                form.applicant_name.data = prefill_app.applicant_name
                form.email.data = prefill_app.email
                form.father_name.data = prefill_app.father_name
                form.roll_number.data = prefill_app.roll_number
                form.class_name.data = prefill_app.class_name
                form.date_of_birth.data = prefill_app.date_of_birth
                form.address.data = prefill_app.address
                form.phone_number.data = prefill_app.phone_number
                # Don't prefill content as it will likely be different for each application
                flash('Form pre-filled with existing student information. Please review and update as needed.', 'info')
        except:
            pass  # If any error occurs, just ignore prefill
    
    if form.validate_on_submit():
        # Create new application
        new_application = Application(
            applicant_name=form.applicant_name.data,
            email=form.email.data,
            father_name=form.father_name.data,
            roll_number=form.roll_number.data,
            class_name=form.class_name.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
            phone_number=form.phone_number.data,
            content=form.content.data,
            status='pending'
        )
        db.session.add(new_application)
        db.session.commit()
        
        flash('Your application has been submitted successfully! Application ID: ' + str(new_application.id), 'success')
        # Redirect to the success page with the application ID
        return redirect(url_for('view_application', application_id=new_application.id))
    
    return render_template('submit_application.html', form=form, existing_applications=existing_applications)

# Admin login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        # For simplicity, we'll use a hardcoded username/password
        # In a real application, you would authenticate against a user database
        if form.username.data == 'admin' and form.password.data == 'admin123':
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

# Dashboard for application management (requires login)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    search_form = ApplicationSearchForm()
    query = None
    
    if search_form.validate_on_submit():
        query = search_form.search_query.data
    else:
        # Handle GET request with query parameter
        query = request.args.get('query', '')
        if query:
            search_form.search_query.data = query
            
    if query:
        # Search by name or roll number
        applications = Application.query.filter(
            db.or_(
                Application.applicant_name.ilike(f'%{query}%'),
                Application.roll_number.ilike(f'%{query}%')
            )
        ).order_by(Application.created_at.desc()).all()
    else:
        applications = Application.query.order_by(Application.created_at.desc()).all()
    
    return render_template('dashboard.html', applications=applications, search_form=search_form)

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