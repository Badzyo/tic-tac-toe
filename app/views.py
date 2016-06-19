import random
from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.models import User, Game, GameUser, GameMove
from app import forms


@app.route("/")
@login_required
def index():
    games_in_wait = Game.query.filter_by(state=Game.game_state['waiting_for_players']).limit(5)
    games_in_progress = Game.query.filter(Game.state.in_([Game.game_state['player_one_turn'],
                                                          Game.game_state['player_two_turn']])).limit(5)
    return render_template('index.html', games_in_progress=games_in_progress, games_in_wait=games_in_wait)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = forms.LoginForm(request.form)
    else:
        form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.get_authenticated_user(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html', login_form=form)


@app.route("/logout", methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = forms.RegisterForm(request.form)
    else:
        form = forms.RegisterForm()

    if form.validate_on_submit():
        user = User(form.username.data, form.password.data, form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)

    # Redirect to homepage, if user is successfully authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return render_template('register.html', register_form=form)


@app.route("/game/new", methods=['GET', 'POST'])
@login_required
def new_game():
    if request.method == 'POST':
        form = forms.NewGameForm(request.form)
    else:
        form = forms.NewGameForm()

    if form.validate_on_submit():
        game = Game(field_size=form.size.data, win_length=form.rule.data)
        db.session.add(game)
        user_order = random.choice([GameUser.user_game_role['player_one'],
                                    GameUser.user_game_role['player_two']])
        game_user = GameUser(user=current_user, game=game, user_role=user_order)
        db.session.add(game_user)
        db.session.commit()
        return redirect(url_for('show_game', game_id=game.id))

    return render_template('new_game.html', new_game_form=form)


@app.route("/game/<int:game_id>", methods=['GET'])
@login_required
def show_game(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('game.html', game=game)


@login_manager.user_loader
def load_user(userid):
    return User.get_user_by_id(userid)
