from connection import ConnectionClosed
from tile import Tile
from eval import count_of_tiles_yaku

class Player:

	def __init__(self, server, name):
		self.name = name
		self.server = server
		self.score = 25000
		self.can_drop_tile = False
		self.drop_zone = []

	def set_neighbours(self, left, right, across):
		self.left_player = left
		self.right_player = right
		self.across_player = across

	def set_wind(self, wind):
		self.wind = wind

	def set_game(self, game, hand):
		self.game = game
		self.hand = hand

	def other_players(self):
		return [ self.left_player, self.right_player, self.across_player ]

	def move(self, tile):
		self.hand.append(tile)
		self.can_drop_tile = True

	def other_move(self, player):
		pass

	def player_dropped_tile(self, player, tile):
		pass

	def hand_actions(self):
		options = []
		if count_of_tiles_yaku(self.hand) > 0:
			options.append("Tsumo")
		return options

	def round_end(self, player, win_type, payment, scores, total_fans):
		pass

class NetworkPlayer(Player):

	def __init__(self, server, name, connection):
		Player.__init__(self, server, name)
		self.connection = connection

	def process_messages(self):
		try:
			message = self.connection.read_message()
			while message:
				self.process_message(message)
				message = self.connection.read_message()
		except ConnectionClosed, e:
			self.server.player_leaved(self)

	def tick(self):
		self.process_messages()

	def round_is_ready(self):
		msg = {}
		msg["message"] = "ROUND"
		msg["left"] = self.left_player.name
		msg["right"] = self.right_player.name
		msg["across"] = self.across_player.name
		msg["my_wind"] = self.wind.name
		msg["round_wind"] = self.game.round_wind.name
		msg["dora"] = self.game.doras[0].name
		msg["hand"] = " ".join( [ tile.name for tile in self.hand ] )
		self.connection.send_dict(msg)

	def move(self, tile):
		Player.move(self, tile)
		actions = " ".join(self.hand_actions())
		self.connection.send_message(message = "MOVE", tile = tile.name, actions = actions)

	def other_move(self, player):
		Player.other_move(self, player)
		self.connection.send_message(message = "OTHER_MOVE", wind = player.wind.name)

	def process_message(self, message):
		name = message["message"]

		if name == "DROP" and self.can_drop_tile:
			self.can_drop_tile = False
			tile = Tile(message["tile"])
			self.hand.remove(tile)
			self.drop_zone.append(tile)
			self.server.state.drop_tile(self, tile)
			return

		if name == "TSUMO":
			if not self.can_drop_tile or "Tsumo" not in self.hand_actions():
				print "Tsumo is not allowed"
				return
			self.server.declare_win(self, "Tsumo")
			self.can_drop_tile = False
			return

		print "Unknown message " + str(message) + " from player: " + self.name

	def player_dropped_tile(self, player, tile):
		self.connection.send_message(message = "DROPPED", wind = player.wind.name, tile = tile.name)

	def round_end(self, player, win_type, payment, scores):
		msg = {}
		msg["message"] = "ROUND_END"
		msg["payment"] = payment
		msg["wintype"] = win_type
		msg["player"] = player.wind.name
		msg["total_fans"] = sum(map(lambda r: r[1], scores))
		msg["score_items"] = ";".join(map(lambda sc: "%s %s" % (sc[0], sc[1]), scores))
		self.connection.send_dict(msg)
