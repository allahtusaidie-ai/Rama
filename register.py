from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import get_db_connection

# Tunatengeneza Blueprint
register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Kuficha password kwa usalama (Hashing)
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Kuchomeka data kwenye database
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, hashed_password))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Usajili umefanikiwa! Karibu uingie (Login).', 'success')
            return redirect(url_for('login')) # Itampeleka kwenye login.py baadaye
            
        except Exception as e:
            flash(f'Hitilafu imetokea: {str(e)}', 'danger')
            
    return render_template('register.html')
