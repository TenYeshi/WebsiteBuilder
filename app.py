import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify

# Setup logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Simple in-memory data storage
projects = [
    {
        'id': 1,
        'title': 'Portfolio Website',
        'description': 'A responsive portfolio website built with Flask and Bootstrap.',
        'image_url': 'https://via.placeholder.com/800x600?text=Portfolio+Website'
    },
    {
        'id': 2,
        'title': 'E-commerce Platform',
        'description': 'A full-featured online store with product listings and shopping cart.',
        'image_url': 'https://via.placeholder.com/800x600?text=E-commerce+Platform'
    },
    {
        'id': 3,
        'title': 'Mobile App Design',
        'description': 'UI/UX design for a fitness tracking mobile application.',
        'image_url': 'https://via.placeholder.com/800x600?text=Mobile+App+Design'
    }
]

messages = []

# Routes
@app.route('/')
def home():
    return render_template('index.html', projects=projects)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Simple form processing without WTForms
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_text = request.form.get('message')
        
        if name and email and subject and message_text:
            message = {
                'id': len(messages) + 1,
                'name': name,
                'email': email,
                'subject': subject,
                'message': message_text,
                'read': False,
                'created_at': datetime.now().strftime('%B %d, %Y')
            }
            messages.append(message)
            flash('Your message has been sent!', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all fields', 'danger')
    
    return render_template('contact.html')

# Simple error handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404
