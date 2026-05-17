from flask import Blueprint, render_template, request
from db import get_db_connection

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    # Chukua neno lililoandikwa kwenye box la search (mfano: ?q=vichekesho)
    query = request.args.get('q', '').strip()
    results = []

    if query:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # SQL ya kutafuta kwenye jina (title) au maelezo (description)
        # Linalinganisha herufi hata kama mtumiaji hajaandika neno kamili (LIKE %query%)
        sql = """
            SELECT id, title, description, video_url, poster_url, category 
            FROM content 
            WHERE title LIKE %s OR description LIKE %s
            ORDER BY created_at DESC
        """
        search_term = f"%{query}%"
        cursor.execute(sql, (search_term, search_term))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()

    return render_template('search.html', query=query, results=results)
