from flask import Flask, render_template, request, jsonify, session, redirect
import json
import os
import secrets
from flask_cors import CORS
from routes.api import api_bp

app = Flask(__name__)
# Set a secret key for session management
app.secret_key = secrets.token_hex(16)
# Enable CORS
CORS(app, supports_credentials=True)

# Register API blueprint
app.register_blueprint(api_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/profile')
def profile_page():
    if not session.get('user'):
        return redirect('/login')
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)