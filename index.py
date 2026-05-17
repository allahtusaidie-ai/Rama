from flask import Flask, render_template
from flask_login import LoginManager
import os
from check_ban import init_security

app = Flask(__name__)
# ... kodi nyingine ...

# Washa mfumo wa ulinzi
init_security(app)

# ... blueprints nyingine ...

# Import Blueprints kutoka kwenye faili tulizotengeneza
from register import register_bp
from login import login_bp, User # Hakikisha User class ipo kwenye login.py
from logout import logout_bp
from forgot_password import forgot_password_bp
from db import get_db_connection
from sizani import sizani_bp
app.register_blueprint(sizani_bp)
from movie import movie_bp
app.register_blueprint(movie_bp)
from games import games_bp
app.register_blueprint(games_bp)
from islamic import islamic_bp
app.register_blueprint(islamic_bp)
from rama import rama_bp
app.register_blueprint(rama_bp)
from ramadhana import ramadhana_bp
app.register_blueprint(ramadhana_bp)
from ai import ai_bp
app.register_blueprint(ai_bp)
from subscription import subscription_bp
from teams import teams_bp
app.register_blueprint(teams_bp)
app.register_blueprint(subscription_bp)
from callback import callback_bp
app.register_blueprint(callback_bp)
# 1. Ingiza (Import) blueprint kutoka kwenye faili la terms.py
from terms import terms_bp
# 2. Msajili (Register) blueprint kwenye app yako ya Flask
app.register_blueprint(terms_bp)
from flask import Blueprint, render_template
from aboutus import aboutus_bp
app.register_blueprint(aboutus_bp)
app = Flask(__name__)
from search import search_bp
# Baada ya app = Flask(__name__)
app.register_blueprint(search_bp)

# Siri ya usalama kwa ajili ya sessions na flash messages
app.secret_key = "siri_yako_ya_siri_sana_123"

# --- USIMAMIZI WA LOGIN (Flask-Login) ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login' # Inampeleka hapa kama akijaribu kufungua peji inayohitaji login
login_manager.login_message = "Tafadhali ingia kwanza ili uone ukurasa huu."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, expiry_date FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    # ... funga connection ...
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['expiry_date'])
    return None

    
    if user_data:
        return User(user_data['id'], user_data['username'])
    return None
class User:
    def __init__(self, id, username, expiry_date=None):
        self.id = id
        self.username = username
        self.expiry_date = expiry_date # Ongeza hii
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Tunachukua pia expiry_date kutoka kwenye database
    cursor.execute("SELECT id, username, expiry_date FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['expiry_date'])
    return None

# --- USAJILI WA BLUEPRINTS ---
# Hapa tunaunganisha zile faili nyingine zote
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(forgot_password_bp)

# --- ROUTES ZA KAWAIDA ---

@app.route('/')
def index():
    """Ukurasa wa nyumbani (Home Page)"""
    return render_template('index.html')

# Hapa tutakuja kuongeza Blueprints za movie.py, games.py n.k. hapo baadaye

# --- KUENDESHA APP ---
if __name__ == '__main__':
    # Tunatumia port 8080 kama ilivyoelekezwa kwenye app.yaml yako
    port = int(os.environ.get("PORT", 8080))
    # debug=True inatusaidia kuona makosa (errors) tunapotengeneza
    app.run(host='0.0.0.0', port=port, debug=True)
