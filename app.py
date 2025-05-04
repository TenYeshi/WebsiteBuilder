import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, 
            static_folder='web/static',
            template_folder='web/templates')
app.secret_key = os.environ.get("SESSION_SECRET", "tenyeshi-portfolio-key")

# Sample projects data (in-memory storage)
projects = [
    {
        'id': 1,
        'title': 'Portfolio Website',
        'description': 'A responsive portfolio website built with Flask and Bootstrap.',
        'image_url': '/static/img/logo.png'
    },
    {
        'id': 2,
        'title': 'E-commerce Platform',
        'description': 'A full-featured online store with product listings and shopping cart.',
        'image_url': '/static/img/logo2.png'
    },
    {
        'id': 3,
        'title': 'Mobile App Design',
        'description': 'UI/UX design for a fitness tracking mobile application.',
        'image_url': '/static/img/logo3.png'
    }
]

# In-memory message storage
messages = []

# Home route
@app.route('/')
def home():
    return render_template('index.html', projects=projects)

# Static page routes
@app.route('/index.html')
def home_page():
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
            # Store message in our in-memory list
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
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all required fields', 'danger')
    
    return render_template('contact.html')

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404