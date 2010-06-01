# Copyright (C) 2009 Stanislav Bohm 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, see 
# <http://www.gnu.org/licenses/>.

import logging
from copy import copy

from connection import ConnectionClosed
from tile import Tile, Pon, Chi, Kan
from eval import count_of_tiles_yaku, find_potential_chi, hand_in_tenpai, riichi_test
from botengine import BotEngine

class Player:

	def __init__(self, server, name):
		self.name = name
		self.server = server
		self.score = 25000
		self.can_drop_tile = False
		self.drop_zone = []
		self.sets = []
		self.riichi = False
		self.ippatsu_move_id = 0

	def player_round_reset(self):
		self.drop_zone = []
		self.sets = []
		self.can_drop_tile = False
		self.riichi = False
		self.ippatsu_move_id = 0

	def set_neighbours(self, left, right, across):
		self.left_player = left
		self.right_player = right
		self.across_player = across

	def set_wind(self, wind):
		self.wind = wind

	def set_round(self, round, hand):
		self.round = round
		self.hand = hand

	def is_dealer(self):
		return self.wind.name == "WE"

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

	def get_specials_yaku(self):
		""" Returns potential special yaku """
		specials = []
		if self.riichi:
			if self.ippatsu_move_id >= self.round.move_id:
				specials.append(('Ippatsu', 1)) 
			specials.append(('Riichi', 1)) 
		return specials

	def round_is_ready(self):
		logging.info("Player '%s' intial hand: %s" % (self.name, self.hand))

	def is_hand_open(self):
		for set in self.sets:
			if not set.closed:
				return True
		return False
	
	def other_condition_for_riichi(self):
		return not self.riichi and self.round.get_remaining_tiles_in_wall() >= 4 and self.score >= 1000 and not self.is_hand_open()

	def hand_actions(self):
		options = []
		if count_of_tiles_yaku(self.hand, self.sets, self.get_specials_yaku(), self.round.round_wind, self.wind) > 0:
			options.append("Tsumo")

		if self.other_condition_for_riichi() and riichi_test(self.hand, self.sets):
			options.append("Riichi")

		for tile in set(self.hand):			
			if self.hand.count(tile) == 4:
				options.append("Kan " + tile.name)
		return options

	def is_furiten(self):
		# TODO
		return False

	def is_tenpai(self):
		return hand_in_tenpai(self.hand, self.sets)

	def steal_actions(self, player, tile):
		options = []
		if self.hand.count(tile) >= 2 and not self.riichi:
			options.append("Pon")

		if player == self.left_player and not self.riichi:
			if find_potential_chi(self.hand, tile):
				options.append("Chi")

		if count_of_tiles_yaku(self.hand + [ tile ], self.sets, self.get_specials_yaku(), self.round.round_wind, 
				self.wind) > 0 and not self.is_furiten():
			options.append("Ron")

		return options

	def round_end(self, player, looser, win_type, payment_name, scores, minipints, diffs, looser_riichi, ura_dora_indicators, end_of_game):
		pass

	def round_end_draw(self, winners, loosers, payment_diffs, end_of_game):
		pass

	def closed_kan_played_by_me(self, kan, new_tile, dora_indicator):
		self.new_hand_tile(new_tile)

	def stolen_tile(self, player, from_player, action, opened_set, tile):
		if self.ippatsu_move_id:
			self.ippatsu_move_id = -100 # Round is interrupeted

		if player == self:
			my_set = copy(opened_set)
			my_set.closed = False

			tiles = my_set.tiles()
			tiles.remove(tile)
			for t in tiles:
				self.hand.remove(t)
	
			self.sets.append(my_set)
			self.can_drop_tile = True

	def drop_tile(self, tile):
		self.hand.remove(tile)
		self.drop_zone.append(tile)
		self.server.state.drop_tile(self, tile)

	def riichi_played_this_turn(self):
		return self.riichi and self.ippatsu_move_id - 4  == self.round.move_id

	def play_riichi(self):
		self.riichi = True
		self.ippatsu_move_id = self.round.move_id + 4
		self.score -= 1000
		self.round.on_riichi(self)

	def play_closed_kan(self, tile):
		kan = Kan(tile)
		kan.closed = True
		for t in kan.tiles():
			self.hand.remove(t)
		self.sets.append(kan)
		self.round.closed_kan_played(self, kan)

	def __str__(self):
		return self.name

	def __repr__(self):
		return "<P: %s>" % self.name


class NetworkPlayer(Player):

	def __init__(self, server, name, connection):
		Player.__init__(self, server, name)
		self.connection = connection
		self.potential_chi = None
		self.steal_tile = None

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
		Player.round_is_ready(self)
		msg = {}
		msg["message"] = "ROUND"
		msg["left"] = self.left_player.name
		msg["right"] = self.right_player.name
		msg["across"] = self.across_player.name
		msg["left_score"] = self.left_player.score
		msg["right_score"] = self.right_player.score
		msg["across_score"] = self.across_player.score
		msg["my_score"] = self.score
		msg["my_wind"] = self.wind.name
		msg["round_wind"] = self.round.round_wind.name
		msg["dora_indicator"] = self.round.dora_indicators[0].name
		msg["hand"] = " ".join( [ tile.name for tile in self.hand ] )
		self.connection.send_dict(msg)

	def move(self, tile):
		Player.move(self, tile)
		actions = ";".join(self.hand_actions())
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
			self.drop_tile(tile)
			return

		if name == "READY":
			self.server.player_is_ready(self)
			return

		if name == "STEAL":
			action = message["action"]
			if "chi_choose" in message:
				chi_tile = Tile(message["chi_choose"])
				for s, marker in self.potential_chi:
					if marker == chi_tile:
						opened_set = s
						break
			else:
				opened_set = Pon(self.steal_tile)

			self.potential_chi = None
			self.steal_tile = None
			self.server.player_try_steal_tile(self, action, opened_set)
			return

		if name == "TSUMO":
			if not self.can_drop_tile or "Tsumo" not in self.hand_actions():
				logging.error("Tsumo is not allowed")
				return
			self.server.declare_win(self, None, "Tsumo")
			self.can_drop_tile = False
			return

		if name == "RIICHI":
			if not self.can_drop_tile or "Riichi" not in self.hand_actions():
				logging.error("Riichi is not allowed")
				return
			self.play_riichi()
			return

		if name == "CLOSED_KAN":
			tile = Tile(message["tile"])
			self.play_closed_kan(tile)
			return


		s = "Unknown message " + str(message) + " from player: " + self.name
		print s
		logging.error(s)

	def closed_kan_played_by_me(self, kan, new_tile, dora_indicator):
		Player.closed_kan_played_by_me(self, kan, new_tile, dora_indicator)
		msg = {}
		msg["message"] = "CLOSED_KAN"
		msg["tile"] = kan.tile.name
		msg["player"] = self.wind.name
		msg["new_tile"] = new_tile.name
		msg["dora_indicator"] = dora_indicator.name
		msg["actions"] = ";".join(self.hand_actions())
		self.connection.send_dict(msg)

	def closed_kan_played_by_other(self, player, kan, dora_indicator):
		msg = {}
		msg["message"] = "CLOSED_KAN"
		msg["player"] = player.wind.name
		msg["tile"] = kan.tile.name
		msg["dora_indicator"] = dora_indicator.name
		self.connection.send_dict(msg)

	def player_dropped_tile(self, player, tile):
		if self != player:
			actions = self.steal_actions(player, tile)
		else:
			actions = []		

		chi_choose = ""

		if actions:
			self.steal_tile = tile
			if "Chi" in actions:
				self.potential_chi = find_potential_chi(self.hand, tile)
				choose_tiles = [ t.name for set, t in self.potential_chi ]
				chi_choose = ";".join(choose_tiles)
			actions.append("Pass")

		msg_actions = ";".join(actions)
		msg = { "message" : "DROPPED", 
				"wind" : player.wind.name, 
				"tile" : tile.name, 
				"chi_choose" : chi_choose,
				"actions" : msg_actions }
		self.connection.send_dict(msg)
		
		if not actions:
			# This should be called after sending DROPPED, because it can cause new game state
			self.server.player_is_ready(self) 

	def player_played_riichi(self, player):
		self.connection.send_message(message = "RIICHI", player = player.wind.name)

	def round_end(self, player, looser, win_type, payment_name, scores, minipoints, payment_diffs, looser_riichi, ura_dora_indicators, end_of_game):
		msg = {}
		msg["message"] = "ROUND_END"
		msg["payment"] = payment_name
		msg["wintype"] = win_type
		msg["player"] = player.wind.name
		msg["total_fans"] = sum(map(lambda r: r[1], scores))
		msg["minipoints"] = minipoints
		msg["looser_riichi"] = looser_riichi
		msg["score_items"] = ";".join(map(lambda sc: "%s %s" % (sc[0], sc[1]), scores))
		msg["ura_dora_indicators"] = " ".join([ tile.name for tile in ura_dora_indicators ])
		msg["end_of_game"] = end_of_game
		msg["winner_hand"] = " ".join( [ tile.name for tile in player.hand ] )
		msg["winner_sets"] = ";".join( [ set.tiles_as_string() for set in player.sets ] )

		for player in self.server.players:
			msg[player.wind.name + "_score"] = player.score 
			msg[player.wind.name + "_payment"] = payment_diffs[player]
	
		self.connection.send_dict(msg)

	def round_end_draw(self, winners, loosers, payment_diffs, end_of_game):
		msg = {}
		msg["message"] = "DRAW"
		msg["tenpai"] = " ".join((player.wind.name for player in winners))
		msg["not_tenpai"] = " ".join((player.wind.name for player in loosers))
		msg["end_of_game"] = end_of_game

		for player in self.server.players:
			msg[player.wind.name + "_score"] = player.score 
			msg[player.wind.name + "_payment"] = payment_diffs[player]

		self.connection.send_dict(msg)
	
	def stolen_tile(self, player, from_player, action, opened_set, stolen_tile):
		Player.stolen_tile(self, player, from_player, action, opened_set, stolen_tile)
		msg = { "message" : "STOLEN_TILE",
				"action" : action,
				"player" : player.wind.name,
				"from_player" : from_player.wind.name,
				"tiles" : " ".join([tile.name for tile in opened_set.tiles()]),
				"stolen_tile" : stolen_tile.name
		}
		self.connection.send_dict(msg)

	def server_quit(self):
		pass


bot_names = (name for name in [ "Panda", "Saki", "Yogi" ])


class BotPlayer(Player):

	def __init__(self, server):
		Player.__init__(self, server, bot_names.next())
		self.engine = BotEngine()
		self.action = None

	def tick(self):
		if self.action:
			self.action()

	def server_quit(self):
		self.engine.shutdown()

	def move(self, tile):
		Player.move(self, tile)
		actions = self.hand_actions()
		if "Tsumo" in actions:
			self.server.declare_win(self, None, "Tsumo")
			return
		elif self.riichi:
			self.drop_tile(tile)
		else:
			self._set_basic_state()
			self.engine.question_discard_and_target()
			self.action = self.action_discard

	def action_discard(self):
		action = self.engine.get_string()
		if action:
			self.action = None
			tile = self.engine.get_tile(True)
			target = self.engine.get_tiles(True)
			
			if action == "Kan":
				self.play_closed_kan(tile)
			else:
				if self.riichi_allowed and self.other_condition_for_riichi():
					h = copy(self.hand)
					h.remove(tile)
					for t in h:
						if t in target:
							target.remove(t)
					if len(target) == 1 and self.round.hidden_tiles_for_player(self).count(target[0]) > 1 and hand_in_tenpai(h, []): 
						# If target is 1 tile away and this tile is more then 1 in "game"
						self.play_riichi()
				self.drop_tile(tile)

	def action_steal(self):
		set_or_pass = self.engine.get_set_or_pass()
		if set_or_pass:
			self.action = None
			if set_or_pass == "Pass":
				self.server.player_is_ready(self)
			else:
				self.server.player_try_steal_tile(self, set_or_pass.get_name(), set_or_pass)

	def _set_basic_state(self):
		self.engine.set_hand(self.hand)
		self.engine.set_wall(self.round.hidden_tiles_for_player(self))
		self.engine.set_sets(self.sets)
		self.engine.set_turns(self.round.get_remaining_turns_for_player(self))

	def player_dropped_tile(self, player, tile):
		if self != player:
			actions = self.steal_actions(player, tile)
			if "Ron" in actions:
				self.server.player_try_steal_tile(self, "Ron", None)
			elif actions:
				sets = []
				if "Pon" in actions:
					sets.append(Pon(tile))
				if "Chi" in actions:
					sets += [ set for set, t in find_potential_chi(self.hand, tile) ]
				self._set_basic_state()
				self.engine.question_steal(tile, sets)
				self.action = self.action_steal
			else:
				self.server.player_is_ready(self)
		else:
				self.server.player_is_ready(self)


	def round_end(self, player, looser, win_type, payment_name, scores, minipints, diffs, looser_riichi, ura_doras_indicators, end_of_game):
		self.server.player_is_ready(self)

	def round_end_draw(self, winners, loosers, diffs, end_of_game):
		self.server.player_is_ready(self)

	def round_is_ready(self):
		Player.round_is_ready(self)
		self.engine.set_doras(self.round.doras)
		self.engine.set_round_wind(self.round.round_wind)
		self.engine.set_player_wind(self.wind)
		self.riichi_allowed = self.round.roll_dice(2) == 1
		logging.info("Bot.riichi_allowed for %s: %s", self.name, self.riichi_allowed)

	def stolen_tile(self, player, from_player, action, set, tile):
		Player.stolen_tile(self, player, from_player, action, set, tile)

		if self == player:
			self._set_basic_state()
			self.engine.question_discard_and_target()
			self.action = self.action_discard

	def player_played_riichi(self, player):
		pass

	def closed_kan_played_by_me(self, kan, new_tile, dora_indicator):
		Player.closed_kan_played_by_me(self, kan, new_tile, dora_indicator)
		self._set_basic_state()
		self.engine.question_discard_and_target()
		self.action = self.action_discard

	def closed_kan_played_by_other(self, player, kan, dora_indicator):
		pass
