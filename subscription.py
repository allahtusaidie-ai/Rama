import os
import hmac
import hashlib
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv(dotenv_path="malipo.env")

subscription_bp = Blueprint('subscription', __name__)

PESAPAL_CONSUMER_KEY = os.getenv("PESAPAL_CONSUMER_KEY")
PESAPAL_CONSUMER_SECRET = os.getenv("PESAPAL_CONSUMER_SECRET")
PESAPAL_URL = os.getenv("PESAPAL_URL")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER", "255743898018")
PESAPAL_IPN_ID = os.getenv("PESAPAL_IPN_ID")  # IPN ID kutoka PesaPal dashboard

PESAPAL_FEE_PERCENTAGE = 0.035  

def get_pesapal_token():
    if not PESAPAL_CONSUMER_KEY or not PESAPAL_CONSUMER_SECRET:
        return None
        
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "consumer_key": PESAPAL_CONSUMER_KEY,
        "consumer_secret": PESAPAL_CONSUMER_SECRET
    }
    try:
        response = requests.post(f"{PESAPAL_URL}/Auth/RequestToken", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("token")
    except requests.exceptions.RequestException:
        pass
    return None

def generate_secure_hash(user_id, timestamp):
    msg = f"{user_id}-{timestamp}".encode('utf-8')
    return hmac.new(PESAPAL_CONSUMER_SECRET.encode('utf-8'), msg, hashlib.sha256).hexdigest()[:16]

def trigger_automatic_payout(amount_to_send, reference):
    token = get_pesapal_token()
    if not token:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Boresha kiasi cha pesa kiwe na decimal mbili tu
    amount_to_send = round(float(amount_to_send), 2)

    # Muundo sahihi wa PesaPal V3 B2C API Request
    payout_payload = {
        "source_account": "MERCHANT_WALLET",
        "destination_channel": "MOBILE_MONEY",
        "reference": f"PAYOUT-{reference}",
        "recipients": [
            {
                "phone_number": MY_PHONE_NUMBER,
                "amount": amount_to_send,
                "currency": "TZS",
                "description": "RAMADHANA Ent Payout"
            }
        ]
    }

    try:
        # ENDPOINT SAHIHI: PesaPal v3 inatumia /B2C/RequestPayment kwa ajili ya kutoka wallet kwenda kwa simu
        payout_url = f"{PESAPAL_URL}/B2C/RequestPayment"
        response = requests.post(payout_url, json=payout_payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_data = response.json()
            # PesaPal B2C mara nyingi inarudisha status kama "Success" au "200" kwenye majibu ya ndani
            if res_data.get("status") == "Success" or res_data.get("status") == "200":
                return True
            else:
                print(f"Payout Declined by PesaPal: {res_data}")
    except Exception as e:
        print(f"Critical Payout Error: {str(e)}")
    return False

@subscription_bp.route('/subscription')
@login_required
def subscription_page():
    return render_template('subscription.html')

@subscription_bp.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    amount_raw = request.form.get('amount')
    plan = request.form.get('plan')
    
    try:
        amount = float(amount_raw)
        if amount not in [500.0, 5000.0]:
            flash("Kiasi cha malipo hakitambuliki!", "danger")
            return redirect(url_for('subscription.subscription_page'))
    except (ValueError, TypeError):
        flash("Malipo batili!", "danger")
        return redirect(url_for('subscription.subscription_page'))

    token = get_pesapal_token()
    if not token:
        flash("Mfumo wa malipo unafanyiwa matengenezo, tafadhali jaribu tena baadae.", "danger")
        return redirect(url_for('subscription.subscription_page'))

    timestamp = int(datetime.now().timestamp())
    secure_hash = generate_secure_hash(current_user.id, timestamp)
    reference = f"RAMA-{current_user.id}-{timestamp}-{secure_hash}"
    
    payload = {
        "id": reference,
        "currency": "TZS",
        "amount": amount,
        "description": f"Kifurushi cha {plan} - {current_user.username}",
        "callback_url": url_for('subscription.payment_callback', _external=True),
        "notification_id": PESAPAL_IPN_ID,  
        "billing_address": {
            "email_address": current_user.email if hasattr(current_user, 'email') else "support@ramadhana.com",
            "first_name": current_user.username
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{PESAPAL_URL}/Transactions/SubmitOrderRequest", json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return redirect(response.json().get("redirect_url"))
        else:
            flash("Imeshindwa kuandaa ukurasa wa malipo. Jaribu tena.", "danger")
    except requests.exceptions.RequestException:
        flash("Tatizo la mtandao limetokea. Jaribu tena.", "danger")
    
    return redirect(url_for('subscription.subscription_page'))

@subscription_bp.route('/payment-callback')
@login_required
def payment_callback():
    tracking_id = request.args.get('OrderTrackingId')
    merchant_reference = request.args.get('OrderMerchantReference')
    
    if not tracking_id or not merchant_reference:
        abort(400)

    try:
        parts = merchant_reference.split('-')
        if len(parts) == 4 and parts[0] == "RAMA":
            user_id = int(parts[1])
            timestamp = int(parts[2])
            received_hash = parts[3]
            
            expected_hash = generate_secure_hash(user_id, timestamp)
            if not hmac.compare_digest(received_hash, expected_hash) or user_id != current_user.id:
                flash("Uthibitishaji wa muamala umeshindikana.", "danger")
                return redirect(url_for('subscription.subscription_page'))
        else:
            abort(400)
    except Exception:
        abort(400)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Kuzuia Replay Attack
        cursor.execute("SELECT id FROM transactions WHERE tracking_id = %s", (tracking_id,))
        already_processed = cursor.fetchone()
        if already_processed:
            cursor.close()
            conn.close()
            flash("Muamala huu tayari umeshughulikiwa.", "warning")
            return redirect(url_for('index'))

        token = get_pesapal_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        status_url = f"{PESAPAL_URL}/Transactions/GetTransactionStatus?orderTrackingId={tracking_id}"
        
        response = requests.get(status_url, headers=headers, timeout=15)
        if response.status_code == 200:
            res = response.json()
            
            if res.get("payment_status_description") == "Completed":
                amount = float(res.get("amount"))
                
                makato = amount * PESAPAL_FEE_PERCENTAGE
                pesa_kwenda_kwako = amount - makato
                
                cursor.execute("SELECT expiry_date FROM users WHERE id = %s", (current_user.id,))
                user_data = cursor.fetchone()
                
                current_expiry = user_data.get('expiry_date') if user_data else None
                now = datetime.now()

                base_date = current_expiry if current_expiry and current_expiry > now else now

                if amount >= 5000.0:
                    new_expiry = base_date + timedelta(days=30)
                    plan_msg = "Kifurushi cha Mwezi kimeongezwa."
                else:
                    new_expiry = base_date + timedelta(hours=24)
                    plan_msg = "Kifurushi cha Siku kimeongezwa."

                try:
                    cursor.execute("UPDATE users SET expiry_date = %s WHERE id = %s", (new_expiry, current_user.id))
                    
                    cursor.execute(
                        "INSERT INTO transactions (tracking_id, merchant_reference, user_id, amount, net_amount, status) VALUES (%s, %s, %s, %s, %s, %s)",
                        (tracking_id, merchant_reference, current_user.id, amount, pesa_kwenda_kwako, 'Completed')
                    )
                    conn.commit()
                    
                    # Tupa pesa moja kwa moja kwenye simu yako ya mkononi (Instant Payout)
                    payout_success = trigger_automatic_payout(pesa_kwenda_kwako, merchant_reference)
                    
                    if payout_success:
                        flash(f"Malipo yamefanikiwa! {plan_msg} Salio la Tsh {pesa_kwenda_kwako:.2f} limehamishwa kwenda kwenye simu yako.", "success")
                    else:
                        flash(f"Malipo yamefanikiwa! {plan_msg}. (Uhamisho wa kwenda kwenye simu yako unashughulikiwa na usimamizi).", "info")
                        
                except Exception as e:
                    if conn:
                        conn.rollback()
                    print(f"Database Transaction Error: {str(e)}")
                    flash("Tatizo la kiufundi lilitokea wakati wa kuhifadhi data.", "danger")
                finally:
                    cursor.close()
                    conn.close()
                
                return redirect(url_for('index'))
                
    except requests.exceptions.RequestException as e:
        print(f"PesaPal Status Request Failed: {str(e)}")
        flash("Imeshindwa kuwasiliana na PesaPal kuthibitisha malipo.", "danger")
    except Exception as e:
        print(f"General Callback Error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()
        
    flash("Malipo hayajakamilika au yamesitishwa.", "warning")
    return redirect(url_for('subscription.subscription_page'))
