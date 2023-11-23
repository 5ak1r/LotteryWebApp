# IMPORTS
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db, requires_roles
from lottery.forms import DrawForm
from models import Draw
from flask_login import current_user, login_required
from sqlalchemy.orm import make_transient

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
@login_required
@requires_roles('user')
def lottery():
    return render_template('lottery/lottery.html', name=current_user.firstname)


# view all draws that have not been played
@lottery_blueprint.route('/create_draw', methods=['POST'])
@login_required
@requires_roles('user')
def create_draw():
    form = DrawForm()

    if form.validate_on_submit():
        # sorts the integers from lowest to highest
        numbers = sorted([form.number1.data,
                        form.number2.data,
                        form.number3.data,
                        form.number4.data,
                        form.number5.data,
                        form.number6.data])
        # combine integers into a single string
        submitted_numbers = " ".join(map(str, numbers))
        # create a new draw with the form data.
        '''
        Commenting out Symmetric Encryption
        new_draw = Draw(user_id=current_user.id, numbers=submitted_numbers, master_draw=False, lottery_round=0, draw_key=current_user.draw_key)
        '''
        new_draw = Draw(user_id=current_user.id, numbers=submitted_numbers, master_draw=False, lottery_round=0, public_key=current_user.public_key)
        # add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # re-render lottery.page
        flash('Draw %s submitted.' % submitted_numbers)
        return redirect(url_for('lottery.lottery'))

    return render_template('lottery/lottery.html', name=current_user.firstname, form=form)


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
@requires_roles('user')
def view_draws():
    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(been_played=False, user_id=current_user.id).all()

    # if playable draws exist
    if len(playable_draws) != 0:
        # does not change the values of the database
        # decrypt all the draws for viewability
        for j in playable_draws:
            make_transient(j)
            j.view_draw(current_user.private_key)
            #j.view_draw(current_user.draw_key)
        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@login_required
@requires_roles('user')
def check_draws():
    # get played draws
    played_draws = Draw.query.filter_by(been_played=True, user_id=current_user.id).all()

    # if played draws exist
    if len(played_draws) != 0:
        # does not change the values of the database
        # decrypt the draws for viewability
        for j in played_draws:
            make_transient(j)
            j.view_draw(current_user.private_key)
        return render_template('lottery/lottery.html', results=played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
@requires_roles('user')
def play_again():
    Draw.query.filter_by(been_played=True, master_draw=False).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


