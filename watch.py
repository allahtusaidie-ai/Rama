from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from db import get_db_connection

watch_bp = Blueprint('watch', __name__)

def has_active_subscription():
    """Kazi yake ni kuangalia kama muda wa malipo haujaisha"""
    if not current_user.is_authenticated:
        return False
    
    if current_user.expiry_date is None:
        return False
    
    # Linganisha muda wa sasa na muda wa kuisha malipo
    return datetime.now() < current_user.expiry_date

@watch_bp.route('/watch/<int:content_id>')
@login_required
def watch_content(content_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Tunatafuta movie/maudhui kwenye database
    cursor.execute("SELECT * FROM content WHERE id = %s", (content_id,))
    content = cursor.fetchone()
    cursor.close()
    conn.close()

    if not content:
        flash("Maudhui hayapatikani.", "danger")
        return redirect(url_for('index'))

    # Kuangalia kama ana kifurushi hai
    subscription_status = has_active_subscription()

    return render_template('watch.html', 
                           content=content, 
                           has_active_subscription=subscription_status)
