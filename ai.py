from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
import os

# Tunatengeneza Blueprint ya AI
ai_bp = Blueprint('ai', __name__)

def tafuta_jibu(swali):
    """Kazi yake ni kusoma maarifa.txt na kulinganisha na swali la mtumiaji"""
    swali = swali.lower()
    # Pata path sahihi ya faili la maarifa.txt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_ya_faili = os.path.join(base_dir, 'maarifa.txt')
    
    try:
        if not os.path.exists(path_ya_faili):
            return "Samahani, faili langu la maarifa halijapatikana."

        with open(path_ya_faili, 'r', encoding='utf-8') as f:
            mistari = f.readlines()
        
        # Jaribu kutafuta mstari unaoendana na maneno ya mtumiaji
        for mstari in mistari:
            # Kama neno lolote la maana lipo kwenye mstari, toa jibu hilo
            maneno_ya_swali = swali.split()
            for neno in maneno_ya_swali:
                if len(neno) > 3 and neno in mstari.lower():
                    return mstari.strip()
                    
        return "Samahani, sijaelewa swali lako. Unaweza kuuliza kuhusu malipo, vifurushi, au jinsi ya kuanza."
    
    except Exception as e:
        return f"Hitilafu imetokea: {str(e)}"

@ai_bp.route('/ai-chat', methods=['GET', 'POST'])
def ai_chat():
    if request.method == 'POST':
        data = request.get_json()
        swali_la_mtumiaji = data.get('message', '')

        # Logic ya ziada: Kama mtumiaji ameuliza kuhusu hali yake ya malipo
        if "kifurushi" in swali_la_mtumiaji.lower() or "muda" in swali_la_mtumiaji.lower():
            if current_user.is_authenticated:
                status = f"Kifurushi chako kitaisha tarehe: {current_user.expiry_date}" if current_user.expiry_date else "Hauna kifurushi hai."
                return jsonify({"reply": status})
            else:
                return jsonify({"reply": "Tafadhali ingia (Login) ili nikupe taarifa za kifurushi chako."})

        # Tafuta jibu la kawaida kwenye maarifa.txt
        jibu = tafuta_jibu(swali_la_mtumiaji)
        return jsonify({"reply": jibu})
    
    return render_template('ai_chat.html')
