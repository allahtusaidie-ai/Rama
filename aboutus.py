from flask import Blueprint, render_template

# Tengeneza Blueprint kwa ajili ya ukurasa wa "Kuhusu Sisi"
aboutus_bp = Blueprint('aboutus', __name__)

@aboutus_bp.route('/about-us')
def aboutus_page():
    # Taarifa za msingi za kampuni
    kampuni_info = {
        "jina": "RAMADHANA Entertainment",
        "mwaka": 2026,
        "maono": "Kuwa jukwaa namba moja la burudani ya kidijitali Afrika Mashariki na Tanzania."
    }

    # Takwimu za tovuti kuonyesha ukubwa wa jukwaa
    stats = [
        {"count": "100+", "label": "Movies & Tamthilia"},
        {"count": "50+", "label": "Games za Kisasa"},
        {"count": "10k+", "label": "Watumiaji Wanaofurahia"},
        {"count": "24/7", "label": "Huduma Iko Hewani"}
    ]
    
    # Maadili au Nguzo Kuu za jukwaa lako
    core_values = [
        {
            "title": "Burudani ya Ndani",
            "desc": "Maudhui yote yamenunuliwa maalum kwa ajili ya soko la Tanzania, yakizingatia simulizi za kipekee na tamthilia kali."
        },
        {
            "title": "Gharama Nafuu",
            "desc": "Kuhakikisha kila mtanzania anapata burudani ya dhahabu kwa bei ya chini kabisa (Tsh 500 kwa siku au Tsh 5,000 kwa mwezi)."
        },
        {
            "title": "Uendeshaji Bora",
            "desc": "Michango yenu inasaidia kuweka seva zetu hewani masaa 24 na kulipia domain name ili usikose burudani wakati wowote."
        }
    ]
    
    return render_template('aboutus.html', info=kampuni_info, stats=stats, values=core_values)

