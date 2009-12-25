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


import time 

from states import LobbyState, ScoreState
from player import BotPlayer
from game import Game

class Server:

	def __init__(self, port):
		self.players = []
		self.players.append(BotPlayer(self))
		self.players.append(BotPlayer(self))
		self.players.append(BotPlayer(self))
		self.game = None
		self.round = None
		self.state = LobbyState(self, port)
		self.state.enter_state()

	def set_state(self, state):
		self.state.leave_state()
		self.state = state
		self.state.enter_state()

	def start_new_game(self):
		self.game = Game(self.players, None)

	def start_new_round(self, rotate_players):
		self.round = self.game.new_round(rotate_players)

	def add_player(self, player):
		self.players.append(player)

	def remove_player(self, player):
		self.players.remove(player)

	def player_leaved(self, player):
		self.state.player_leaved(player)
		self.remove_player(player)
	
	def player_tick(self):
		for player in self.players[:]:
			player.tick()

	def run(self):
		try:
			while True:
				self.state.tick()
				self.player_tick()
				time.sleep(0.07)
		finally:
			self.server_quit()

	def server_quit(self):
		for player in self.players:
			player.server_quit()

	def declare_win(self, player, looser, wintype):
		self.set_state(ScoreState(self, player, looser, wintype))

	def player_is_ready(self, player):
		self.state.player_is_ready(player)

	def player_try_steal_tile(self, player, action, opened_set):
		self.state.player_try_steal_tile(player, action, opened_set)

server = Server(4500)
server.run()
