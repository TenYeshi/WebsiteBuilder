from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong, random key in production

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Static page routes
@app.route('/index.html')
def home_page():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/login.html', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'signup':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            # Perform signup logic here (e.g., save to DB)
            flash(f"User {username} signed up successfully!", "success")
            return redirect(url_for('auth'))

        elif form_type == 'login':
            email = request.form.get('email')
            password = request.form.get('password')

            if email == "admin" and password == "123":
                session['user'] = 'admin'
                flash("Welcome Admin!", "success")
                return redirect(url_for('dashboard'))  # Redirect to dashboard after successful login
            else:
                flash("Invalid admin credentials", "danger")
                return redirect(url_for('auth'))  # Redirect back to the login form

    return render_template('login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # TODO: Lookup user, generate token, send email, etc.
        flash(f'Password reset link sent to {email}', 'info')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    if session.get('user') == 'admin':
        return render_template('dashboard.html')  # You’ll create this file
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('auth'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You’ve been logged out.", "info")
    return redirect(url_for('auth'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
