from flask import Blueprint, render_template
from db import get_db_connection

# Tunatengeneza Blueprint ya Sizani
sizani_bp = Blueprint('sizani', __name__)

@sizani_bp.route('/sizani')
def sizani_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Tunachukua maudhui ambayo category yake ni 'sizani'
    query = "SELECT * FROM content WHERE category = 'sizani' ORDER BY created_at DESC"
    cursor.execute(query)
    sizani_items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('sizani.html', sizani_items=sizani_items)
