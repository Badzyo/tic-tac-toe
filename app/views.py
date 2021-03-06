import random
from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc
from app import app, db, login_manager, forms
from app.models import User, Game, GameMove
from app.decorators import not_in_game


@app.route("/")
@login_required
@not_in_game
def index():
    games_in_wait = Game.query.filter_by(state=Game.game_state['waiting_for_players']).limit(5)
    games_in_progress = Game.query.filter_by(state=Game.game_state['in_progress']).limit(5)
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
        flash('Welcome to the Tic-Tac-Toe!', 'success')
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
        # generate random players order in game
        user_order = random.choice([1, 2])
        if user_order == 1:
            game = Game(field_size=form.size.data, win_length=form.rule.data, player1=current_user)
        else:
            game = Game(field_size=form.size.data, win_length=form.rule.data, player2=current_user)

        db.session.add(game)
        db.session.commit()
        return redirect(url_for('show_game', game_id=game.id))

    return render_template('new_game.html', new_game_form=form)


@app.route("/game/join/<int:game_id>", methods=['POST'])
@login_required
def join_game(game_id):
    game = Game.query.get_or_404(game_id)

    if game.player1_id and game.player2:
        # redirect back to the game if it's full
        flash('Current game is already in progress')
        return redirect(url_for('show_game', game_id=game_id))

    # check available player position in game
    if game.player1_id is None:
        game.player1 = current_user
    else:
        game.player2 = current_user

    game.state = Game.game_state['in_progress']
    db.session.commit()
    return redirect(url_for('show_game', game_id=game_id))


@app.route("/game/flee", methods=['POST'])
@login_required
def flee_game():
    game = current_user.current_game

    # if there is no game to flee, redirect to homepage
    if not game:
        flash('There is no game to flee')
        return redirect(url_for('index'))

    game.state = Game.game_state['finished']
    if game.player1_id == current_user.id:
        opponent = game.player2
        result = Game.game_result['player_two_win']
    else:
        opponent = game.player1
        result = Game.game_result['player_one_win']

    # if there was a second player in a game, let him win
    if opponent:
        game.result = result

    db.session.commit()
    return redirect(url_for('index'))


@app.route("/game/<int:game_id>", methods=['GET'])
@login_required
@not_in_game
def show_game(game_id):
    game = Game.query.get_or_404(game_id)
    if game.player1_id == current_user.id:
        player_number = 1
    elif game.player2_id == current_user.id:
        player_number = 2
    else:
        # Spectator
        player_number = current_user.id + 100  # simple unique spectator id
    return render_template('game.html', game=game, player_number=player_number)


@app.route("/profile/<int:user_id>", methods=['GET'])
@login_required
@not_in_game
def user_profile(user_id):
    last_games_limit = 25
    finished = Game.game_state['finished']
    user = User.get_user_by_id(user_id)
    games = user.games.filter(Game.state == finished)\
        .filter(Game.player1_id)\
        .filter(Game.player2_id)\
        .order_by(desc(Game.id)).limit(last_games_limit)
    return render_template('profile.html', games=games, user=user)


@app.route("/gamearchive/<int:game_id>", methods=['GET'])
@login_required
@not_in_game
def show_archived_game(game_id):
    game = Game.query.get_or_404(game_id)
    player_number = current_user.id + 100  # unique spectator id
    template = 'archive_game.html'
    if game.state != Game.game_state['finished']:
        template = 'game.html'
    return render_template(template, game=game, player_number=player_number)


@app.route("/game/<int:game_id>/json", methods=['GET'])
def get_game_data(game_id):
    game = Game.query.get_or_404(game_id)
    players = []
    for index, player_name in enumerate((game.player1.username, game.player2.username)):
        player = {
            'name': player_name,
            'player_number': index + 1
        }
        players.append(player)
    moves = list(map(GameMove.dic, game.moves))
    return jsonify(moves=moves, players=players)


@login_manager.user_loader
def load_user(userid):
    return User.get_user_by_id(userid)
