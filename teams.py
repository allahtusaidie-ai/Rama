from flask import Blueprint, render_template

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/teams')
def teams_page():
    # Unaweza kuweka data hizi kwenye Database pia, lakini hapa ni rahisi zaidi
    team_members = [
        {
            "name": "RAMADHAN ABDALLA ABDILLAH",
            "role": "CEO & Founder",
            "image": "https://via.placeholder.com/150", # Weka link ya picha yako
            "bio": "Msimamizi mkuu na mwanzilishi wa jukwaa la Ramadhana."
        },
        {
            "name": "RAMADHAN ABDALLA ABDILLAH",
            "role": "Software Engineer",
            "image": "https://via.placeholder.com/150",
            "bio": "Mtaalamu wa mifumo ya malipo na usalama wa tovuti."
        },
        {
            "name": "RAMADHAN ABDALLA ABDILLAH",
            "role": "Sizani Specialist",
            "image": "https://via.placeholder.com/150",
            "bio": "Anahusika na kuchuja simulizi kali na Movies za kisasa."
        }
    ]
    return render_template('teams.html', team=team_members)

