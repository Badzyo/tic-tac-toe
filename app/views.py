import random
from flask import render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Game, GameUser, GameMove
from app.decorators import not_in_game


@app.route("/")
@login_required
@not_in_game
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
        flash('Can not find this combination of username and password')

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
        flash('Welcome to the Tic-Tac-Toe!')
        return redirect(url_for('index'))

    return render_template('register.html', register_form=form)


@app.route("/game/new", methods=['GET', 'POST'])
@login_required
@not_in_game
def new_game():
    if request.method == 'POST':
        form = forms.NewGameForm(request.form)
    else:
        form = forms.NewGameForm()

    if form.validate_on_submit():
        game = Game(field_size=form.size.data, win_length=form.rule.data)
        db.session.add(game)

        # generate random players order in game
        user_order = random.choice([GameUser.user_game_role['player_one'],
                                    GameUser.user_game_role['player_two']])

        game_user = GameUser(user=current_user, game=game, user_role=user_order)
        db.session.add(game_user)
        db.session.commit()
        return redirect(url_for('show_game', game_id=game.id))

    return render_template('new_game.html', new_game_form=form)


@app.route("/game/join/<int:game_id>", methods=['POST'])
@login_required
def join_game(game_id):
    game = Game.query.get_or_404(game_id)
    players = game.users.all()

    # redirect back to the game if it's full
    if len(players) != 1:
        flash('Current game is already in progress')
        return redirect(url_for('show_game', game_id=game_id))

    # check available player position in game
    if players[0].user_game_role == GameUser.user_game_role['player_one']:
        available_role = GameUser.user_game_role['player_two']
    else:
        available_role = GameUser.user_game_role['player_one']

    game_user = GameUser(user=current_user, game=game, user_role=available_role)
    db.session.add(game_user)
    db.session.commit()
    return redirect(url_for('show_game', game_id=game_id))


@app.route("/game/flee", methods=['POST'])
@login_required
def flee_game():
    game = current_user.current_game

    # if there is no game to flee, redirect to homepage
    if not game:
        flash('There is no game to flee')
        redirect(url_for('index'))

    game.state = Game.game_state['finished']
    opponent = game.users.filter(User != current_user).first()

    # if there was a second player in a game, let him win
    if opponent:
        if opponent.user_role == GameUser.user_game_role['player_one']:
            result = Game.game_result['player_one_win']
        else:
            result = Game.game_result['player_two_win']
        game.result = result

    db.session.commit()
    return redirect(url_for('index'))


@app.route("/game/<int:game_id>", methods=['GET'])
@login_required
@not_in_game
def show_game(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('game.html', game=game)


@login_manager.user_loader
def load_user(userid):
    return User.get_user_by_id(userid)
