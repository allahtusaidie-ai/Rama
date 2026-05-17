from flask import Blueprint, render_template

# Kutengeneza Blueprint kwa ajili ya ukurasa wa Vigezo na Masharti (Terms)
terms_bp = Blueprint('terms', __name__)

@terms_bp.route('/terms')
def terms_page():
    """
    Route hii inafungua ukurasa wa masharti na vigezo (terms.html).
    Inaonyesha taarifa za umiliki wa RAMADHANA Entertainment nchini Tanzania,
    pamoja na maelezo ya uendeshaji wa seva na domain name.
    """
    return render_template('terms.html')

