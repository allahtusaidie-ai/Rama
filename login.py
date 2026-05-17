from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user
from db import get_db_connection

# Tunatengeneza Blueprint ya login
login_bp = Blueprint('login', __name__)

# Hapa tunafanya mfano wa User object kwa ajili ya Flask-Login
class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Tafuta mtumiaji kwenye database
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user_data and check_password_hash(user_data['password'], password):
            # Angalia kama mtumiaji amefungiwa (check_ban logic)
            if user_data['is_banned']:
                flash('Akaunti yako imefungiwa. Wasiliana na admin.', 'danger')
                return redirect(url_for('login.login'))
            
            # Tengeneza user object na login
            user_obj = User(user_data['id'], user_data['username'])
            login_user(user_obj)
            
            flash(f'Karibu tena {username}!', 'success')
            return redirect(url_for('index')) # Inapeleka home page
        else:
            flash('Jina la mtumiaji au nenosiri si sahihi.', 'danger')
            
    return render_template('login.html')
