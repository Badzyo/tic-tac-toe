from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash


def not_in_game(func):
    """
    If you decorate a view with this, it will ensure that the current user is
    not in game right now.

        @app.route('/')
        @not_in_game
        def index():
            pass

    If current user is in game, he will be redirected to game view.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        game = current_user.current_game
        if game:
            try:
                game_id = kwargs['game_id']
                if game.id == game_id and func.__name__ == 'show_game':
                    return func(*args, **kwargs)
            except KeyError:
                pass
            flash('You can not go away, while you are in game. Press "Flee" if you want to end the game')
            return redirect(url_for('show_game', game_id=game.id))
        else:
            return func(*args, **kwargs)
    return decorated_view
