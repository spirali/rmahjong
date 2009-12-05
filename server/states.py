
from message import check_message
from player import NetworkPlayer
from connection import Connection
from dictprotocol import DictProtocol
from game import Game


class LobbyState:

	def __init__(self, server, port):
		self.server = server
		self.port = port

	def enter_state(self):
		self.listen_connection = Connection()
		self.listen_connection.bind_and_listen(self.port, True)
		self.connections = []

	def leave_state(self):
		self.listen_connection.close()
		self.listen_connection = None

		for conn in self.connections:
			conn.close()
		self.connections = []

	def process_messages(self):
		for connection in self.connections[:]:
			msg = connection.read_message()
			if msg:
				self.connections.remove(connection)
				if check_message(msg, "LOGIN"):
					self.new_player(connection, msg)
				else:
					connection.close()

	def try_new_connections(self):
			conn = self.listen_connection.accept()
			if conn:
				dp = DictProtocol(conn)
				self.connections.append(dp)
				print "New peer: " + str(conn.get_peer_name())

		
	def new_player(self, connection, msg):
		print "New network player: " + msg["user_name"]
		connection.send_message(message="WELCOME", version = "0.0")
		player = NetworkPlayer(self.server, msg["user_name"], connection)
		self.server.add_player(player)

		if len(self.server.players) == 4:
			self.init_game()

	def init_game(self):
		players = self.server.players
		from game import FakeGame
		game = FakeGame(players)
		self.server.set_game(game)
		self.server.set_state(PlayerMoveState(self.server, game.get_east_player()))

	def tick(self):
		self.try_new_connections()
		self.process_messages()

	def player_leaved(self, player):
		print "Player %s leaved" % player.name


class GenericGameState:
	
	def __init__(self, server):
		self.server = server

	def player_leaved(self, player):
		# TODO: Terminate game
		pass

	def tick(self):
		pass

	def enter_state(self):
		pass

	def leave_state(self):
		pass


class PlayerMoveState(GenericGameState):

	def __init__(self, server, player):
		GenericGameState.__init__(self, server)
		self.player = player
		player.move(server.game.pick_random_tile())
		for p in player.other_players():
			p.other_move(player)

	def drop_tile(self, player, tile):
		assert player == self.player
		for p in self.server.players:
			p.player_dropped_tile(player, tile)
		self.server.set_state(PlayerMoveState(self.server, self.player.right_player))


class StealTileState(GenericGameState):
	
	def __init__(self, server, player, droped_tile):
		GenericGameState.__init__(self, server)
		self.player = player
		self.droped_tile = droped_tile


class ScoreState(GenericGameState):
	
	def __init__(self, server, player, win_type):
		GenericGameState.__init__(self, server)
		self.player = player
		self.win_type = win_type

	def enter_state(self):
		GenericGameState.enter_state(self)
		self.server.game.end_of_game(self.player, self.win_type)

