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


from tile import all_tiles, east_wind, winds, Tile, dora_from_indicator
from random import Random
from eval import compute_score
from copy import copy

class Game:

	def __init__(self, players, seed):
		self.random = Random(seed)
		self.players = copy(players)
		self.random.shuffle(self.players)
		self.round_id = 0

	def new_round(self, rotate_players):
		self.round_id += 1

		# Rotate players
		if rotate_players:
			east_player = self.players[0]
			self.players.remove(east_player)
			self.players.append(east_player)

		return Round(self.players, self.random)


class Round:

	def __init__(self, players, random):
		self.random = random
		self.init_round()
		self.init_players(players)

	def get_dealer(self):
		return self.players[0]

	def init_round(self):
		self.wall = 4 * all_tiles
		self.dora_indicators = [ self.pick_random_tile() ]
		self.doras = [ dora_from_indicator(self.dora_indicators[0]) ]
		self.round_wind = east_wind
		self.active_player = None

	def init_players(self, players):
		for i, player in enumerate(players):
			left = players[(i + 3) % 4]
			right = players[(i + 1) % 4]
			across = players[(i + 2) % 4]
			player.set_neighbours(left, right, across)
			player.set_round(self, self.get_hand())
			player.set_wind(winds[i])
			player.round_is_ready()
		self.players = players

	def pick_random_tile(self):
		tile = self.random.choice(self.wall)
		self.wall.remove(tile)
		return tile

	def set_active_player(self, player):
		self.active_player = player

	def get_hand(self):
		return [ self.pick_random_tile() for i in xrange(13) ]

	def get_remaining_turns(self):
		return len(self.wall) - 14 + len(self.dora_indicators)

	def is_draw(self):
		return self.get_remaining_turns() < 1

	def get_remaining_turns_for_player(self, player):
		players = self.players
		i = (4 + players.index(player) - players.index(self.active_player) - 1) % 4
		return (self.get_remaining_turns() - i) / 4

	def hidden_tiles_for_player(self, player):
		return player.left_player.hand + player.right_player.hand + player.across_player.hand + self.wall

	def end_of_round(self, winner, looser, wintype):
		payment, scores, minipoints  = compute_score(winner.hand, winner.open_sets, wintype, self.doras, False, self.round_wind, winner.wind)
		diffs = self.payment_diffs(payment, wintype, winner, looser)
		
		for player in diffs:
			player.score += diffs[player]		

		if wintype == "Tsumo":
			if payment[1][1] != 0:
				payment_name = payment[0] + " " + str(payment[1][0]) + "/" + str(payment[1][1])
			else:
				payment_name = payment[0] + " " + str(payment[1][0])
		else:
			payment_name = payment[0] + " " + str(payment[1])
			
		for player in self.players:
			player.round_end(winner, looser, wintype, payment_name, scores, minipoints, diffs)

	def end_of_round_draw(self):
		winners = [ player for player in self.players if player.is_tenpai() ]
		loosers = [ player for player in self.players if not player.is_tenpai () ]
		diffs = {}

		if len(winners) != 0 and len(loosers) != 0:
			l_payment = -3000 / len(loosers)
			w_payment = 3000 / len(winners)
			for player in winners: 
				diffs[player] = w_payment
				player.score += w_payment

			for player in loosers: 
				diffs[player] = l_payment
				player.score += l_payment
		else:
			for player in self.players:
				diffs[player] = 0

		for player in self.players:
			player.round_end_draw(winners, loosers, diffs)
		
		return winners, loosers

	def payment_diffs(self, payment, wintype, winner, looser):
		others = winner.other_players()
		if wintype == "Ron":
			others.remove(looser)
			return { others[0]: 0, others[1]: 0, winner: payment[1], looser: -payment[1] }
		else:
			s = 0
			d = {}
			po, pe = payment[1]
			for player in others:
				if player.is_dealer():
					d[player] = - pe
					s += pe
				else:
					d[player] = - po
					s += po
			d[winner] = s
			return d


class DebugRound(Round):
	
	def __init__(self, players):
		def tiles(strs):
			return map(Tile, strs)

		hands = [
			#[ "WW", "DG", "DG", "DG", "DR", "DR", "DR", "DW", "DW", "DW", "B8", "B7", "B6" ],
			[ "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "DW", "DW" ],
			[ "C8", "C7", "C5", "C2", "C4", "DR", "DR", "DR", "DW", "DW", "DW", "B7", "B7" ],
			[ "C8", "C9", "C5", "C6", "C4", "C2", "C3", "C1", "DW", "DW", "DW", "B7", "B7" ],
			#[ "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "DW", "DW" ],
			[ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C7", "C8" ],
			[ "DG", "DG", "DR", "C7", "C8", "DW", "DW", "DR", "B1", "B2", "B2", "B2", "B1" ],
			[ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2" ],
			[ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C9" ],
		]

		r = [ "DR", "WW", "WN", "P9", "DR", "C2", "C9" ]
	
		self.hands = map(tiles, hands) 
		self.rnd = tiles(r)
		Round.__init__(self, players)

		for h in self.hands:
			for t in h:
				if t in self.wall:
					self.wall.remove(t)

	def get_hand(self):
		hand = self.hands[0]
		del self.hands[0]
		return hand

	def pick_random_tile(self):
		tl = self.rnd[0]
		del self.rnd[0]
		return tl
