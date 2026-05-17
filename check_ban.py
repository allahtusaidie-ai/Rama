from flask import request, abort, flash, redirect, url_for
from flask_login import current_user
from db import get_db_connection

# Orodha ya maneno hatari yanayoweza kutumika kwenye SQL Injection au XSS
DANGEROUS_KEYWORDS = [
    "<script>", "javascript:", "onclick", "onerror", "alert(", 
    "DROP TABLE", "DELETE FROM", "SELECT * FROM users", "UNION SELECT", 
    "OR 1=1", "INSERT INTO", "--", "';"
]

def security_layer():
    """
    Kazi yake ni kukagua kila data inayotumwa na mtumiaji
    ili kuzuia mashambulizi ya kodi hatari (XSS/SQL Injection)
    """
    # 1. Kagua data za fomu (POST) na link (GET)
    request_data = str(request.form.to_dict()) + str(request.args.to_dict())
    
    for keyword in DANGEROUS_KEYWORDS:
        if keyword.lower() in request_data.lower():
            # Kama neno hatari limepatikana, zuia shambulio
            abort(403, description="Shambulio la kiusalama limegunduliwa!")

    # 2. Kagua kama mtumiaji amefungiwa (Ban Check)
    if current_user.is_authenticated:
        if getattr(current_user, 'is_banned', False):
            # Unaweza pia kutoa logout hapa
            return "Akaunti yako imefungiwa. Huwezi kuendelea."

def init_security(app):
    """Unganisha ulinzi huu na Flask App"""
    @app.before_request
    def run_security_checks():
        # Usikague ulinzi kwenye faili za static (CSS/JS) ili website isikwame
        if request.path.startswith('/static'):
            return
            
        check = security_layer()
        if check:
            return check
