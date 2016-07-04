from app.models import Game, GameMove
from app import db


class ActiveGameHandler:
    def __init__(self, game_id, player_number, socket):
        self.id = game_id
        self.game = Game.query.get(game_id)
        self.started = False
        self.players = dict()
        player = self.game.get_player_by_number(player_number)
        self.players[player_number] = (socket, player)
        self.moves = self.game.moves
        self.max_moves = self.game.field_size ** 2
        self.field = GameField(self.game.field_size, self.moves)
        self.current_player = 1

    @property
    def is_empty(self):
        return not self.players

    def connect_user(self, player_number, socket):
        """
        Add new player's socket to the players dictionary
        """
        player = self.game.get_player_by_number(player_number)
        self.connect_notification(player, player_number)
        self.players[player_number] = (socket, player)
        self.send_game_data(player_number)
        if not self.started:
            if {1, 2}.issubset(self.players):
                self.start_game()

    def disconnect_user(self, player_number):
        """
        Remove player's socket from the players dictionary
        """
        try:
            socket, player = self.players.pop(player_number, None)
            print(player)  # TODO: remove
            # notify all about disconnect
            self.disconnect_notification(player, player_number)
        except TypeError:
            # current player is not in players
            pass

    def notify_all(self, message):
        """
        Send broadcast message to all online users in game
        """
        for socket, _ in self.players.values():
            socket.write_message(message)

    def disconnect_notification(self, player, player_number):
        """
        Notify other users in game about current user disconnect
        """
        data = self.init_message('disconnect')
        data['user'] = {
            'username': player.username,
            'role': player_number
        }
        self.notify_all(data)

    def connect_notification(self, player, player_number):
        """
        Notify other users in game about current user connect
        """
        data = self.init_message('connect')
        data['user'] = {
            'username': player.username,
            'role': player_number
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
        data['players'] = []
        data['spectators'] = []
        print(self.players)
        for key, value in self.players.items():
            if key in (1, 2):
                data['players'].append(value[1].username)
            else:
                data['spectators'].append(value[1].username)
        data['moves'] = []
        for move in self.moves:
            data['moves'].append({
                'x': move.x,
                'y': move.y,
                'player': move.player_number
            })
        socket.write_message(data)

    def apply_move(self, player_number, cell):
        """
        Apply received move to the game,
        update game status, and then notify other users about this update
        """
        move = GameMove(game_id=self.game.id, player_number=player_number, x=cell[0], y=cell[1])
        self.moves.append(move)
        self.field.add_move(move)

        win_line = self.check_win()
        if win_line:
            self.game.state = Game.game_state['finished']
            self.game.result = player_number
        if len(self.moves) == self.max_moves and not win_line:
            self.game.state = Game.game_state['finished']
            self.game.result = Game.game_result['draw']
        self._set_next_player()
        if self.game.state == Game.game_state['finished']:
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
        if self.game.game_state == Game.game_state['finished']:
            self.current_player = None
        else:
            self.current_player = (self.current_player % 2) + 1

    def send_chat_message(self, sender, message):
        """
        Send message to all online users in a game
        """
        data = self.init_message('chat')
        data['chat'] = {
            'from': sender.username,
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
        socket, player = self.players.pop(player_number, None)
        socket.close(reason='Flee')
        data = self.init_message('flee')
        data['user'] = {
            'username': player.username,
            'role': player_number
        }
        self.notify_all(data)

    @staticmethod
    def init_message(message):
        data = dict()
        data['message'] = message
        return data

    def check_win(self):
        """
        Finds out whether last move led to victory.
        If it was the winning move, returns a winning line
        """
        move = self.moves[-1]
        for line in self.field.player_line_getters:
            if len(line(move)) >= self.game.win_length:
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
                    self.grid[move.x][move.y] = move.player_number
                except IndexError:
                    pass

    def add_move(self, move):
        """
        Place a new move at the grid
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
