from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import get_db_connection
from functools import wraps

ramadhana_bp = Blueprint('ramadhana', __name__)

# Decorator ya kuzuia watu wasio admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash("Hauna ruhusa ya kufungua ukurasa huu.", "danger")
            return redirect(url_for('rama.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@ramadhana_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Kupata idadi ya watumiaji
    cursor.execute("SELECT COUNT(id) as total FROM users")
    user_count = cursor.fetchone()['total']
    
    # Kupata maudhui yote yaliyowekwa hivi karibuni
    cursor.execute("SELECT * FROM content ORDER BY created_at DESC LIMIT 5")
    recent_content = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('ramadhana.html', user_count=user_count, recent_content=recent_content)

@ramadhana_bp.route('/admin/add-content', methods=['POST'])
@login_required
@admin_required
def add_content():
    title = request.form['title']
    description = request.form['description']
    video_url = request.form['video_url']
    poster_url = request.form['poster_url']
    category = request.form['category']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO content (title, description, video_url, poster_url, category) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (title, description, video_url, poster_url, category))
    conn.commit()
    
    cursor.close()
    conn.close()
    flash("Maudhui yameongezwa kwa mafanikio!", "success")
    return redirect(url_for('ramadhana.admin_dashboard'))
@ramadhana_bp.route('/admin/ban-user/<int:user_id>')
@admin_required
def ban_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1 WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Mtumiaji amefungiwa kikamilifu!", "success")
    return redirect(url_for('ramadhana.admin_dashboard'))
