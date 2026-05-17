from flask import Blueprint, render_template, request
from db import get_db_connection

# Tunatengeneza Blueprint ya movie
movie_bp = Blueprint('movie', __name__)

@movie_bp.route('/movies')
def movie_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Tunachukua maudhui yote ambayo ni ya kategoria ya 'movie'
    query = "SELECT * FROM content WHERE category = 'movie' ORDER BY created_at DESC"
    cursor.execute(query)
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('movie.html', movies=movies)
