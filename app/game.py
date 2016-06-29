from app.models import Game, User, GameMove


class ActiveGameHandler:
    def __init__(self, game_id, player_number, socket):
        self.game = Game.query.get(game_id)
        self.players[player_number] = socket