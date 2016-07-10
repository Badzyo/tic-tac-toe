import sqlalchemy
from app.models import Game, GameMove, User
from app import db


class ActiveGameHandler:
    def __init__(self, game_id):
        self.id = game_id
        self.game = IndependentGameObject(game_id)
        self.started = False
        self.players = dict()
        self.max_moves = self.game.field_size ** 2
        self.field = GameField(self.game.field_size, self.game.moves)
        self.current_player = -1

    @property
    def is_empty(self):
        return not self.players

    def connect_user(self, player_number, socket):
        """
        Add new player's socket to the players dictionary
        """
        if player_number in (1, 2) and self.players:
            # to get second player name
            self.game.refresh_from_db()
        player_name = self.game.get_player_by_number(player_number)
        self.connect_notification(player_name, player_number)
        self.players[player_number] = (socket, player_name)
        self.send_game_data(player_number)
        if not self.started and self.game.state == Game.game_state['waiting_for_players']:
            if {1, 2}.issubset(self.players):
                self.start_game()

    def disconnect_user(self, player_number):
        """
        Remove player's socket from the players dictionary
        """
        try:
            socket, player_name = self.players.pop(player_number, None)
            # notify all about disconnect
            self.disconnect_notification(player_name, player_number)
        except TypeError:
            # if current player is not in players
            pass

    def notify_all(self, message):
        """
        Send broadcast message to all online users in game
        """
        for socket, _ in self.players.values():
            socket.write_message(message)

    def disconnect_notification(self, player_name, player_number):
        """
        Notify other users in game about current user disconnect
        """
        data = self.init_message('disconnect')
        data['user'] = {
            'name': player_name,
            'player_number': player_number,
            'online': False
        }
        self.notify_all(data)

    def connect_notification(self, player_name, player_number):
        """
        Notify other users in game about current user connect
        """
        data = self.init_message('connect')
        data['user'] = {
            'name': player_name,
            'player_number': player_number,
            'online': True
        }
        self.notify_all(data)

    def send_game_data(self, player_number):
        """
        Send game data for a newly connected user
        """
        try:
            socket = self.players[player_number][0]
        except KeyError:
            return
        data = self.init_message('initial')
        data['current_player'] = self.current_player
        data['players'] = []
        data['spectators'] = []

        for index, player_name in enumerate((self.game.player1, self.game.player2)):
            player = {
                'name': player_name,
                'player_number': index + 1,
                'online': (index + 1) in self.players
            }
            data['players'].append(player)

        for key, value in self.players.items():
            player_name = value[1]
            if key > 2:
                data['spectators'].append(player_name)
        data['moves'] = self.game.moves
        socket.write_message(data)

    def apply_move(self, player_number, cell):
        """
        Apply received move to the game,
        update game status, and then notify other users about this update
        """
        if player_number != self.current_player:
            # TODO: Notify player to wait for his turn
            return

        # TODO: validate cell data
        x = int(cell[0])
        y = int(cell[1])
        move = GameMove(game_id=self.game.id, player_number=player_number, x=x, y=y)
        self.game.add_move(move)
        self.field.mark_cell(move)

        win_line = self.check_win(move)
        if win_line:
            self.game.state = Game.game_state['finished']
            self.game.result = player_number
        if len(self.game.moves) == self.max_moves and not win_line:
            self.game.state = Game.game_state['finished']
            self.game.result = Game.game_result['draw']
        self._set_next_player()
        if self.game.state == Game.game_state['finished']:
            self.game.write_to_db()
            data = self.init_message('finish')
            data['finish'] = {
                'result': self.game.result,
            }
            if win_line:
                data['finish']['win_line'] = [
                    {
                        'x': win_line[0][0],
                        'y': win_line[0][1]
                    },
                    {
                        'x': win_line[-1][0],
                        'y': win_line[-1][1]
                    }
                ]
        else:
            data = self.init_message('move')
        data['move'] = {
            'x': cell[0],
            'y': cell[1],
            'player': player_number
        }
        db.session.add(move)
        db.session.commit()
        self.notify_all(data)

    def _set_next_player(self):
        """
        Change current_player to the next player after player's move
        """
        if self.game.state == Game.game_state['finished']:
            self.current_player = -1
        else:
            self.current_player = (self.current_player % 2) + 1

    def send_chat_message(self, player_number, message):
        """
        Send message to all online users in a game
        """
        player = self.players.get(player_number, None)
        if player:
            name = player[1]
            data = self.init_message('chat')
            data['chat'] = {
                'from': name,
                'text': message
            }
            self.notify_all(data)

    def start_game(self):
        """
        Start game, and notify all players about it
        """
        self.current_player = 1
        self.started = True
        data = self.init_message('start')
        self.notify_all(data)

    def flee(self, player_number):
        """
        Close socket and notify all about user's fleeing
        """
        socket, player_name = self.players.pop(player_number, None)
        data = self.init_message('flee')
        data['user'] = {
            'name': player_name,
            'player_number': player_number,
            'online': False
        }
        self.notify_all(data)

    @staticmethod
    def init_message(message):
        data = dict()
        data['message'] = message
        return data

    def check_win(self, move):
        """
        Finds out whether last move led to victory.
        If it was the winning move, returns a winning line
        """
        for getter in self.field.player_line_getters:
            line = getter(move)
            if len(line) >= self.game.win_length:
                return line
        return False


class GameField:
    """
    Model of the tik-tak-toe game grid
    """
    def __init__(self, size, moves=None):
        # init grid
        self.grid_size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]

        # place moves at the grid
        if moves:
            for move in moves:
                try:
                    self.grid[move['x']][move['y']] = move['player']
                except IndexError:
                    pass

    def mark_cell(self, move):
        """
        Mark cell as occupied by one of two players
        """
        try:
            self.grid[move.x][move.y] = move.player_number
        except IndexError:
            pass

    def get_player_row_line(self, move):
        """
        Calculates a line of current player's cells, adjoined to nearby player's move in row
        :param move: A move for which a line will be calculated
        :return: A list of player's cells in line. Such as [(0,1),(1,1),(2,1)]
        """
        line = [(move.x, move.y)]
        x = move.x + 1
        y = move.y
        while x < self.grid_size and self.grid[x][y] == move.player_number:
            line.append((x, y))
            x += 1
        x = move.x - 1
        while x >= 0 and self.grid[x][y] == move.player_number:
            line.insert(0, (x, y))
            x -= 1

        return line

    def get_player_column_line(self, move):
        """
        Calculates a line of current player's cells, adjoined to nearby player's move in column
        :param move: A move for which a line will be calculated
        :return: A list of player's cells in line. Such as [(1,0),(1,1),(1,2)]
        """
        line = [(move.x, move.y)]
        x = move.x
        y = move.y + 1
        while y < self.grid_size and self.grid[x][y] == move.player_number:
            line.append((x, y))
            y += 1
        y = move.y - 1
        while y >= 0 and self.grid[x][y] == move.player_number:
            line.insert(0, (x, y))
            y -= 1

        return line

    def get_player_main_diagonal_line(self, move):
        """
        Calculates a line of current player's cells, adjoined to nearby player's move in main diagonal
        :param move: A move for which a line will be calculated
        :return: A list of player's cells in line. Such as [(0,0),(1,1),(2,2)]
        """
        line = [(move.x, move.y)]
        x = move.x + 1
        y = move.y + 1
        while x < self.grid_size \
                and y < self.grid_size \
                and self.grid[x][y] == move.player_number:
            line.append((x, y))
            x += 1
            y += 1
        x = move.x - 1
        y = move.y - 1
        while x >= 0 and y >= 0 and self.grid[x][y] == move.player_number:
            line.insert(0, (x, y))
            x -= 1
            y -= 1

        return line

    def get_player_reverse_diagonal_line(self, move):
        """
        Calculates a line of current player's cells, adjoined to nearby player's move in reverse diagonal
        :param move: A move for which a line will be calculated
        :return: A list of player's cells in line. Such as [(0,2),(1,1),(2,0)]
        """
        line = [(move.x, move.y)]
        x = move.x + 1
        y = move.y - 1
        while x < self.grid_size and y >= 0 \
                and self.grid[x][y] == move.player_number:
            line.append((x, y))
            x += 1
            y -= 1
        x = move.x - 1
        y = move.y + 1
        while x >= 0 and y < self.grid_size \
                and self.grid[x][y] == move.player_number:
            line.insert(0, (x, y))
            x -= 1
            y += 1

        return line

    @property
    def player_line_getters(self):
        getters = [
            self.get_player_row_line,
            self.get_player_column_line,
            self.get_player_main_diagonal_line,
            self.get_player_reverse_diagonal_line
        ]
        return getters


class IndependentGameObject:
    def __init__(self, game_id):
        self.id = game_id
        game = self.get_from_db()

        try:
            self.player1 = game.player1.username
        except AttributeError:
            self.player1 = None

        try:
            self.player2 = game.player2.username
        except AttributeError:
            self.player2 = None

        self.field_size = game.field_size
        self.win_length = game.win_length
        self.state = game.state
        self.result = game.result
        self.moves = []
        for move in game.moves:
            self.add_move(move)

    def refresh_from_db(self):
        game = self.get_from_db()
        if game.player1_id:
            self.player1 = game.player1.username
        if game.player2_id:
            self.player2 = game.player2.username
        self.state = game.state
        self.result = game.result

    def write_to_db(self):
        game = self.get_from_db()
        game.state = self.state
        game.result = self.result
        db.session.commit()

    def get_from_db(self):
        return Game.query.get(self.id)

    def add_move(self, move):
        self.moves.append({
                'player': move.player_number,
                'x': move.x,
                'y': move.y
        })

    def get_player_by_number(self, player_number):
        if player_number == 1:
            return self.player1
        elif player_number == 2:
            return self.player2
        else:
            spectator = User.get_user_by_id(player_number - 100)
            return spectator.username
