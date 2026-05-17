from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from db import get_db_connection
from datetime import datetime

games_bp = Blueprint('games', __name__)

def is_subscribed():
    """Kazi yake ni kuangalia kama mtumiaji amelipia kifurushi"""
    if not current_user.is_authenticated:
        return False
    if current_user.expiry_date is None:
        return False
    return datetime.now() < current_user.expiry_date

@games_bp.route('/games')
def games_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Tunachukua maudhui ya kategoria ya 'games'
    query = "SELECT * FROM content WHERE category = 'games' ORDER BY created_at DESC"
    cursor.execute(query)
    all_games = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Tunatuma pia hali ya malipo (True/False) kwenda kwenye HTML
    subscribed = is_subscribed()
    
    return render_template('games.html', games=all_games, subscribed=subscribed)
