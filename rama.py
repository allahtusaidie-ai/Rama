from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user
from db import get_db_connection
from login import User # Tunatumia User class ile ile

rama_bp = Blueprint('rama', __name__)

@rama_bp.route('/rama', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Tunatafuta mtumiaji ambaye ni Admin tu
        query = "SELECT * FROM users WHERE username = %s AND is_admin = 1"
        cursor.execute(query, (username,))
        admin_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if admin_data and check_password_hash(admin_data['password'], password):
            # Login imefanikiwa
            admin_obj = User(admin_data['id'], admin_data['username'])
            login_user(admin_obj)
            
            flash('Karibu Admin! Unaingia kwenye mfumo wa usimamizi.', 'success')
            return redirect(url_for('ramadhana.admin_dashboard'))
        else:
            flash('Huna ruhusa ya kuingia hapa au nenosiri si sahihi.', 'danger')
            
    return render_template('rama.html')
