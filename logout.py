from flask import Blueprint, redirect, url_for, flash
from flask_login import logout_user, login_required

# Tunatengeneza Blueprint ya logout
logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout')
@login_required # Hii inahakikisha kuwa ni mtu aliyeingia tu ndiye anayeweza kulogout
def logout():
    logout_user() # Hapa tunafuta session ya mtumiaji
    flash('Umetoka kwenye mfumo kwa usalama.', 'info')
    return redirect(url_for('login.login'))
