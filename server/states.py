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
from message import check_message
from player import NetworkPlayer
from connection import Connection
from dictprotocol import DictProtocol
from tile import Chi, Pon
from eval import find_potential_chi

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
				logging.info("New peer: " + str(conn.get_peer_name()))

		
	def new_player(self, connection, msg):
		logging.info("New network player: " + msg["user_name"])
		connection.send_message(message="WELCOME", version = "0.0")
		player = NetworkPlayer(self.server, msg["user_name"], connection)
		self.server.add_player(player)

		if len(self.server.players) == 4:
			self.init_game()

	def init_game(self):
		self.server.start_new_game()
		self.server.start_new_round(False)
		self.server.set_state(PlayerMoveState(self.server, self.server.round.get_dealer()))

	def tick(self):
		self.try_new_connections()
		self.process_messages()

	def player_leaved(self, player):
		logging.info("Player %s leaved" % player.name)


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

	def player_is_ready(self, player):
		pass


class PlayerMoveState(GenericGameState):

	def __init__(self, server, player):
		GenericGameState.__init__(self, server)
		self.player = player

	def enter_state(self):
		logging.debug("PlayerMoveState: %s %s" % (self.player.name, self.player.hand))
		self.server.round.set_active_player(self.player)

		for p in self.player.other_players():
			p.other_move(self.player)
		self.player.move(self.server.round.pick_random_tile())

	def drop_tile(self, player, tile):
		assert player == self.player
		self.server.set_state(StealTileState(self.server, player, tile))


steal_priority = ("Ron", "Pon", "Chi", "Pass")

class StealTileState(GenericGameState):
	
	def __init__(self, server, player, droped_tile):
		GenericGameState.__init__(self, server)
		self.player = player
		self.droped_tile = droped_tile
		self.ready_players = [ (player, "Pass", None) ]

	def enter_state(self):
		logging.debug("StealTileState: %s %s" % (self.player.name, self.player.hand))
		for p in self.server.players:
			p.player_dropped_tile(self.player, self.droped_tile)

	def is_player_ready(self, player):
		return player in map(lambda x: x[0], self.ready_players)

	def player_is_ready(self, player):
		if not self.is_player_ready(player):
			self.ready_players.append((player, "Pass", None))
		self.check_ready_players()

	def player_try_steal_tile(self, player, action, opened_set):
		if not self.is_player_ready(player):
			self.ready_players.append((player, action, opened_set))
		self.check_ready_players()

	def check_ready_players(self):
		if len(self.ready_players) == 4:
			players = self.player.other_players() + [ self.player ]
			self.ready_players.sort(key = lambda i: players.index(i[0]))
			self.ready_players.sort(key = lambda i: steal_priority.index(i[1]))

			logging.debug("Responses on drop: %s" % self.ready_players)

			s_player, s_action, s_chichoose = self.ready_players[0]
			if s_action == "Ron":
				s_player.new_hand_tile(self.droped_tile)
				self.server.declare_win(s_player, self.player, "Ron")
			elif self.server.round.is_draw():
				self.server.set_state(DrawState(self.server))
			elif s_action == "Pass":
				self.server.set_state(PlayerMoveState(self.server, self.player.right_player))
			else:
				state = DropAfterStealState(self.server, s_player, self.player, self.droped_tile, s_action, s_chichoose)
				self.server.set_state(state)


class DropAfterStealState(GenericGameState):

	def __init__(self, server, player, from_player, stolen_tile, action, opened_set):
		GenericGameState.__init__(self, server)
		self.player = player
		self.stolen_tile = stolen_tile
		self.action = action
		self.from_player = from_player
		self.opened_set = opened_set

	def enter_state(self):
		for player in self.server.players:
			player.stolen_tile(self.player, self.from_player, self.action, self.opened_set, self.stolen_tile)

	def drop_tile(self, player, tile):
		assert player == self.player
		self.server.set_state(StealTileState(self.server, player, tile))


class WaitingForReadyPlayersState(GenericGameState):

	def __init__(self, server):
		GenericGameState.__init__(self, server)
		self.ready_players = []

	def player_is_ready(self, player):
		if player not in self.ready_players:
			self.ready_players.append(player)
		if len(self.ready_players) == 4:
			self.all_players_are_ready()

	def all_players_are_ready(self):
		pass


class ScoreState(WaitingForReadyPlayersState):
	
	def __init__(self, server, player, looser, win_type):
		WaitingForReadyPlayersState.__init__(self, server)
		self.player = player
		self.looser = looser
		self.win_type = win_type

	def enter_state(self):
		GenericGameState.enter_state(self)
		logging.info("Score: winner=%s; looser=%s; wintype=%s" % (self.player, self.looser, self.win_type))

		for player in [ self.player ] + self.player.other_players():
			logging.info("Player %s %s %s: " % (player.name, player.hand, player.open_sets))		

		self.server.round.end_of_round(self.player, self.looser, self.win_type)

	def all_players_are_ready(self):
		rotate_players = not self.player.is_dealer()
		self.server.start_new_round(rotate_players)
		self.server.set_state(PlayerMoveState(self.server, self.server.round.get_dealer()))


class DrawState(WaitingForReadyPlayersState):
	
	def __init__(self, server):
		WaitingForReadyPlayersState.__init__(self, server)

	def enter_state(self):
		GenericGameState.enter_state(self)
		winners, loosers = self.server.round.end_of_round_draw()
		self.winners = winners

		logging.info("Draw:")
		for player in winners:
			logging.info("Winner %s %s %s: " % (player.name, player.hand, player.open_sets))		

		for player in loosers:
			logging.info("Looser %s %s %s: " % (player.name, player.hand, player.open_sets))		

	def all_players_are_ready(self):
		rotate_players = self.server.round.get_dealer() not in self.winners
		self.server.start_new_round(rotate_players)
		self.server.set_state(PlayerMoveState(self.server, self.server.round.get_dealer()))
