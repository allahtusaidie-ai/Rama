from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
import requests
from datetime import datetime, timedelta
from db import get_db_connection  # Hakikisha hii inatoka kwenye db.py yako

callback_bp = Blueprint('callback', __name__)

# Taarifa zako za PesaPal (Zilinganishe na zile za process_payment)
PESAPAL_CONSUMER_KEY = "SsuFZOXUYloLodjzecbSp23/2DsVAzBO"
PESAPAL_CONSUMER_SECRET = "SBeZiUcdi3TLoQ2zKDfu+pkpUAM="
PESAPAL_URL = "https://pay.pesapal.com/v3/api"

def get_pesapal_token():
    """Inapata Token ya muda ya kuombea taarifa PesaPal"""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "consumer_key": PESAPAL_CONSUMER_KEY,
        "consumer_secret": PESAPAL_CONSUMER_SECRET
    }
    try:
        response = requests.post(f"{PESAPAL_URL}/Auth/RequestToken", json=payload, headers=headers)
        return response.json().get("token")
    except:
        return None

@callback_bp.route('/payment-callback')
@login_required
def payment_callback():
    # PesaPal inarudisha hizi ID baada ya malipo
    order_tracking_id = request.args.get('OrderTrackingId')
    order_merchant_reference = request.args.get('OrderMerchantReference')

    if not order_tracking_id:
        flash("Muamala haukukamilika vizuri.", "danger")
        return redirect(url_for('subscription.subscription_page'))

    # 1. Pata Token ya kuhakiki muamala
    token = get_pesapal_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 2. Uliza PesaPal: "Je, muamala huu umelipwa kweli?"
    status_url = f"{PESAPAL_URL}/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
    response = requests.get(status_url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        status = result.get("payment_status_description") # Mfano: "Completed"
        amount = result.get("amount")

        # 3. Kama malipo yamekamilika ("Completed"), mpe mtumiaji muda
        if status == "Completed":
            now = datetime.now()
            
            # Angalia kama ni 5,000 (Mwezi) au 500 (Siku)
            if float(amount) >= 5000:
                expiry_date = now + timedelta(days=30)
                plan_name = "Mwezi mmoja"
            else:
                expiry_date = now + timedelta(hours=24)
                plan_name = "Siku moja"

            # 4. Update Database ya mtumiaji
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                query = "UPDATE users SET expiry_date = %s WHERE id = %s"
                cursor.execute(query, (expiry_date, current_user.id))
                conn.commit()
                flash(f"Hongera! Malipo ya Tsh {amount} yamepokelewa. Kifurushi cha {plan_name} kimeanza.", "success")
            except Exception as e:
                conn.rollback()
                flash("Tatizo la database limetokea.", "danger")
            finally:
                cursor.close()
                conn.close()
        else:
            flash(f"Muamala wako una hali ya: {status}. Subiri kidogo au jaribu tena.", "warning")
    else:
        flash("Imeshindwa kuthibitisha malipo kutoka PesaPal.", "danger")

    return redirect(url_for('index'))

