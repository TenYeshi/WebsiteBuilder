import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from forms import ApplicationForm, ApplicationFeedbackForm, LoginForm, RegistrationForm, ApplicationSearchForm

# Create an application status form with Flask-WTF
from flask_wtf import FlaskForm
# Create an application status form
class ApplicationStatusForm(FlaskForm):
    username = StringField('Application ID or Roll Number', validators=[DataRequired()])
    password = PasswordField('Email Address', validators=[DataRequired()])
    submit = SubmitField('Check Status')

# Import removed as welcome generator functionality is no longer needed

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
from models import Project, Message, Application, User, Document

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

# Welcome routes removed as requested

# Word Processor Application
@app.route('/word-processor')
def word_processor():
    """Word processor for creating new applications"""
    mode = request.args.get('mode', 'add')
    application_id = request.args.get('id')
    
    # If in edit mode and application_id provided, get the application
    application = None
    if mode == 'edit' and application_id:
        application = Application.query.get_or_404(application_id)
    
    # Get all applications for the delete mode
    applications = []
    if mode == 'delete':
        applications = Application.query.order_by(Application.created_at.desc()).all()
    
    return render_template('word_processor/index.html', 
                           mode=mode, 
                           application=application,
                           applications=applications)

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

# Login page - handles both admin login and registration
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    
    if login_form.validate_on_submit():
        # Check if user exists and password is correct
        user = User.query.filter_by(username=login_form.username.data).first()
        
        if user and user.check_password(login_form.password.data):
            # Create a session for the user (in a real app, you'd use flask-login)
            flash('Login successful!', 'success')
            # Send admin users to the dashboard
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    # Handle registration form submission
    if registration_form.validate_on_submit():
        # Check if username or email already exists
        username_exists = User.query.filter_by(username=registration_form.username.data).first()
        email_exists = User.query.filter_by(email=registration_form.email.data).first()
        
        if username_exists:
            flash('Username already exists', 'danger')
        elif email_exists:
            flash('Email already registered', 'danger')
        # Check if passwords match
        elif registration_form.password.data != registration_form.confirm_password.data:
            flash('Passwords do not match', 'danger')
        else:
            # Create a new user
            new_user = User(
                username=registration_form.username.data,
                email=registration_form.email.data
            )
            new_user.set_password(registration_form.password.data)
            
            # First user is automatically an admin
            if User.query.count() == 0:
                new_user.is_admin = True
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('login.html', login_form=login_form, registration_form=registration_form)

# Logout route
@app.route('/logout')
def logout():
    # In a real application with flask-login, you would use logout_user()
    # Here we'll just redirect to the home page with a message
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

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

# Check application status for applicants
@app.route('/check-status', methods=['GET', 'POST'])
def check_application_status():
    form = ApplicationStatusForm()
    
    if form.validate_on_submit():
        # Try to find application by ID or roll number
        application_id_or_roll = form.username.data.strip() if form.username.data else ""
        email = form.password.data.strip() if form.password.data else ""
        
        # First check if it's a numeric application ID
        application = None
        try:
            if application_id_or_roll and application_id_or_roll.isdigit():
                application = Application.query.filter_by(
                    id=int(application_id_or_roll),
                    email=email
                ).first()
            
            # If not found by ID, try roll number
            if not application:
                application = Application.query.filter_by(
                    roll_number=application_id_or_roll,
                    email=email
                ).first()
                
            if application:
                flash('Application found! Showing details.', 'success')
                return redirect(url_for('view_application', application_id=application.id))
            else:
                flash('No application found with the provided details. Please check and try again.', 'danger')
        except Exception as e:
            app.logger.error(f"Error checking application status: {e}")
            flash('An error occurred while checking your application. Please try again.', 'danger')
    
    return render_template('check_status.html', form=form)

# API endpoints for document management in word processor
@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all documents or applications based on mode"""
    mode = request.args.get('mode', 'add')
    
    if mode == 'edit' or mode == 'delete':
        # Return list of applications
        applications = Application.query.order_by(Application.created_at.desc()).all()
        return jsonify({
            'success': True,
            'documents': [{
                'id': app.id,
                'title': f"Application #{app.id} - {app.applicant_name}",
                'date': app.created_at.strftime('%Y-%m-%d %H:%M'),
                'type': 'application'
            } for app in applications]
        })
    else:
        # Return list of document templates or regular documents
        documents = Document.query.order_by(Document.created_at.desc()).all()
        return jsonify({
            'success': True,
            'documents': [{
                'id': doc.id,
                'title': doc.title,
                'date': doc.created_at.strftime('%Y-%m-%d %H:%M'),
                'type': 'document'
            } for doc in documents]
        })

@app.route('/api/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID"""
    document = Document.query.get_or_404(document_id)
    return jsonify({
        'success': True,
        'document': {
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'created_at': document.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': document.updated_at.strftime('%Y-%m-%d %H:%M')
        }
    })

@app.route('/api/applications/<int:application_id>', methods=['GET'])
def get_application_document(application_id):
    """Get a specific application by ID"""
    application = Application.query.get_or_404(application_id)
    return jsonify({
        'success': True,
        'document': {
            'id': application.id,
            'title': f"Application #{application.id} - {application.applicant_name}",
            'content': application.content,
            'created_at': application.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': application.updated_at.strftime('%Y-%m-%d %H:%M'),
            'applicant_name': application.applicant_name,
            'email': application.email,
            'father_name': application.father_name,
            'roll_number': application.roll_number,
            'class_name': application.class_name,
            'date_of_birth': application.date_of_birth,
            'address': application.address,
            'phone_number': application.phone_number,
            'status': application.status
        }
    })

@app.route('/api/documents', methods=['POST'])
def save_document():
    """Save a new document or update an existing one"""
    data = request.json
    
    mode = data.get('mode', 'add')
    title = data.get('title', 'Untitled Document')
    content = data.get('content', '')
    document_id = data.get('id')
    
    if mode == 'add':
        # Create a new application from the document
        new_application = Application(
            applicant_name=data.get('applicant_name', 'Unknown'),
            email=data.get('email', 'unknown@example.com'),
            father_name=data.get('father_name', ''),
            roll_number=data.get('roll_number', ''),
            class_name=data.get('class_name', ''),
            date_of_birth=data.get('date_of_birth', ''),
            address=data.get('address', ''),
            phone_number=data.get('phone_number', ''),
            content=content,
            status='pending'
        )
        
        # Create a document and link it to the application
        new_document = Document(
            title=title,
            content=content
        )
        
        db.session.add(new_document)
        db.session.flush()  # Flush to get the document ID
        
        new_application.document_id = new_document.id
        db.session.add(new_application)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document and application saved successfully',
            'document_id': new_document.id,
            'application_id': new_application.id
        })
        
    elif mode == 'edit' and document_id:
        # Update existing application
        application = Application.query.get_or_404(document_id)
        
        # Update application fields
        application.applicant_name = data.get('applicant_name', application.applicant_name)
        application.email = data.get('email', application.email)
        application.father_name = data.get('father_name', application.father_name)
        application.roll_number = data.get('roll_number', application.roll_number)
        application.class_name = data.get('class_name', application.class_name)
        application.date_of_birth = data.get('date_of_birth', application.date_of_birth)
        application.address = data.get('address', application.address)
        application.phone_number = data.get('phone_number', application.phone_number)
        application.content = content
        
        # Update document if it exists
        if application.document_id:
            document = Document.query.get(application.document_id)
            if document:
                document.title = title
                document.content = content
        else:
            # Create a new document if none exists
            new_document = Document(
                title=title,
                content=content
            )
            db.session.add(new_document)
            db.session.flush()
            application.document_id = new_document.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application updated successfully',
            'application_id': application.id
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid request'
    }), 400

@app.route('/api/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """Delete an application and its associated document"""
    application = Application.query.get_or_404(application_id)
    
    # Delete associated document if it exists
    if application.document_id:
        document = Document.query.get(application.document_id)
        if document:
            db.session.delete(document)
    
    db.session.delete(application)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Application deleted successfully'
    })

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404