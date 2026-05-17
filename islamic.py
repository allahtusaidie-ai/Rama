from flask import Blueprint, render_template
from db import get_db_connection

# Tunatengeneza Blueprint ya Islamic
islamic_bp = Blueprint('islamic', __name__)

@islamic_bp.route('/islamic')
def islamic_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Tunachukua maudhui ambayo category yake ni 'islamic'
    query = "SELECT * FROM content WHERE category = 'islamic' ORDER BY created_at DESC"
    cursor.execute(query)
    islamic_items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Tunatuma data kwenye template
    return render_template('islamic.html', items=islamic_items)
