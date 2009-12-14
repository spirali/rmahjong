from connection import ConnectionClosed
from tile import Tile
from eval import count_of_tiles_yaku, find_potential_chi
from copy import copy

class Player:

	def __init__(self, server, name):
		self.name = name
		self.server = server
		self.score = 25000
		self.can_drop_tile = False
		self.drop_zone = []
		self.open_sets = []

	def set_neighbours(self, left, right, across):
		self.left_player = left
		self.right_player = right
		self.across_player = across

	def set_wind(self, wind):
		self.wind = wind

	def set_round(self, round, hand):
		self.round = round
		self.hand = hand

	def other_players(self):
		""" Returns other players in order from right """
		return [ self.right_player, self.across_player, self.left_player ]

	def new_hand_tile(self, tile):
		self.hand.append(tile)

	def move(self, tile):
		self.new_hand_tile(tile)
		self.can_drop_tile = True

	def other_move(self, player):
		pass

	def player_dropped_tile(self, player, tile):
		pass

	def hand_actions(self):
		options = []
		if count_of_tiles_yaku(self.hand, self.open_sets) > 0:
			options.append("Tsumo")
		return options

	def is_furiten(self):
		# TODO
		return False

	def steal_actions(self, player, tile):
		options = []
		if self.hand.count(tile) >= 2:
			options.append("Pon")

		if player == self.left_player:
			if find_potential_chi(self.hand, tile):
				options.append("Chi")

		if count_of_tiles_yaku(self.hand + [ tile ], self.open_sets) > 0 and not self.is_furiten():
			options.append("Ron")

		return options

	def round_end(self, player, win_type, payment, scores, total_fans):
		pass

	def stolen_tile(self, player, from_player, action, set, tile):
		if player == self:
			my_set = copy(set)
			my_set.closed = False
			self.open_sets.append(my_set)
			self.can_drop_tile = True

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
		msg["round_wind"] = self.round.round_wind.name
		msg["dora"] = self.round.doras[0].name
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

		if name == "DROP":
			if not self.can_drop_tile:
				return
			self.can_drop_tile = False
			tile = Tile(message["tile"])
			self.hand.remove(tile)
			self.drop_zone.append(tile)
			self.server.state.drop_tile(self, tile)
			return

		if name == "READY":
			self.server.player_is_ready(self)
			return

		if name == "STEAL":
			action = message["action"]
			if "chi_choose" in message:
				chi_choose = Tile(message["chi_choose"])
			else:
				chi_choose = None
			self.server.player_try_steal_tile(self, action, chi_choose)
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
		if self != player:
			actions = self.steal_actions(player, tile)
		else:
			actions = []		

		chi_choose = ""

		if actions:
			if "Chi" in actions:
				choose_tiles = [ t.name for set, t in find_potential_chi(self.hand, tile) ]
				chi_choose = " ".join(choose_tiles)
			actions.append("Pass")
		else:
			self.server.player_is_ready(self)

		msg_actions = " ".join(actions)
		msg = { "message" : "DROPPED", 
				"wind" : player.wind.name, 
				"tile" : tile.name, 
				"chi_choose" : chi_choose,
				"actions" : msg_actions }
		self.connection.send_dict(msg)

	def round_end(self, player, win_type, payment, scores):
		msg = {}
		msg["message"] = "ROUND_END"
		msg["payment"] = payment
		msg["wintype"] = win_type
		msg["player"] = player.wind.name
		msg["total_fans"] = sum(map(lambda r: r[1], scores))
		msg["score_items"] = ";".join(map(lambda sc: "%s %s" % (sc[0], sc[1]), scores))
		self.connection.send_dict(msg)

	def stolen_tile(self, player, from_player, action, set, tile):
		Player.stolen_tile(self, player, from_player, action, set, tile)
		msg = { "message" : "STOLEN_TILE",
				"action" : action,
				"player" : player.wind.name,
				"from_player" : from_player.wind.name,
				"tiles" : " ".join([tile.name for tile in set.tiles()]),
				"stolen_tile" : tile.name
		}
		self.connection.send_dict(msg)
