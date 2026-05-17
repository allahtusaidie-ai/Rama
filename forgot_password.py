from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import get_db_connection

# Tunatengeneza Blueprint
forgot_password_bp = Blueprint('forgot_password', __name__)

@forgot_password_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Nenosiri hazioani (Passwords do not match).', 'danger')
            return render_template('forgot_password.html')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Angalia kama email ipo
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Badilisha nenosiri (Update)
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
            flash('Nenosiri limebadilishwa kwa mafanikio. Sasa unaweza kuingia.', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('login.login'))
        else:
            flash('Barua pepe hiyo haijajisajili kwenye mfumo wetu.', 'warning')
            cursor.close()
            conn.close()
            
    return render_template('forgot_password.html')
