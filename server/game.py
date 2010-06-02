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

from tile import all_tiles, east_wind, winds, Tile, dora_from_indicator
from random import Random
from eval import compute_score

class Game:

	def __init__(self, players, seed):
		self.random = Random(seed)
		self.players = copy(players)
		#self.random.shuffle(self.players)
		self.rotate_players() # DEBUG
		self.rotate_players() # DEBUG
		#self.rotate_players() # DEBUG
		self.first_east_player = self.players[0]
		self.round_wind = east_wind
		logging.info("Players order: " + str(self.players))
		self.round_id = 0

	def rotate_players(self):
		east_player = self.players[0]
		self.players.remove(east_player)
		self.players.append(east_player)
	
	def new_round(self, rotate_players):
		self.round_id += 1

		# Rotate players
		if rotate_players:
			self.rotate_players()
			if self.players[0] == self.first_east_player:
				self.next_round_wind()

		return Round(self.players, self.random, self.round_wind, self.is_potential_last_round())

	def next_round_wind(self):
		self.round_wind = winds[(1 + winds.index(self.round_wind)) % 4]

	def is_potential_last_round(self):
		return self.round_wind == winds[1] and self.players[0].right_player == self.first_east_player


class Round:

	def __init__(self, players, random, round_wind, potential_last):
		self.random = random
		self.round_wind = round_wind
		self.potential_last = potential_last
		self.init_round()
		self.init_players(players)
		logging.info("Round is ready")

	def get_dealer(self):
		return self.players[0]

	def init_round(self):
		self.wall = 4 * all_tiles
		self.dora_indicators = [ self.pick_random_tile() ]
		self.doras = [ dora_from_indicator(self.dora_indicators[0]) ]
		self.active_player = None
		self.move_id = 0
		self.last_innterruption = 0
		logging.info("New round")
		logging.info("Dora indicator: " + str(self.dora_indicators[0]))
		logging.info("Round wind: " + str(self.round_wind))

	def init_players(self, players):
		for i, player in enumerate(players):
			player.player_round_reset()
			left = players[(i + 3) % 4]
			right = players[(i + 1) % 4]
			across = players[(i + 2) % 4]
			player.set_neighbours(left, right, across)
			player.set_round(self, self.get_hand())
			player.set_wind(winds[i])
			player.round_is_ready()

		self.original_score = {}
		for player in players:
			self.original_score[player] = player.score
		self.players = players


	def pick_random_tile(self):
		tile = self.random.choice(self.wall)
		self.wall.remove(tile)
		return tile

	def set_active_player(self, player):
		self.active_player = player

	def get_hand(self):
		return [ self.pick_random_tile() for i in xrange(13) ]

	def get_remaining_tiles_in_wall(self):
		return len(self.wall) - 14 + len(self.dora_indicators)

	def is_draw(self):
		return self.get_remaining_tiles_in_wall() < 1

	def on_riichi(self, player):
		for p in self.players:
			p.player_played_riichi(player)

	def get_remaining_turns_for_player(self, player):
		players = self.players
		i = (4 + players.index(player) - players.index(self.active_player) - 1) % 4
		return (self.get_remaining_tiles_in_wall() - i) / 4

	def hidden_tiles_for_player(self, player):
		return player.left_player.hand + player.right_player.hand + player.across_player.hand + self.wall

	def move_interrputed(self):
		self.last_innterruption = self.move_id

	def closed_kan_played(self, player, kan):
		dora_indicator = self.pick_random_tile()
		dora = dora_from_indicator(dora_indicator)
		self.dora_indicators.append(dora_indicator)
		self.doras.append(dora)
		
		player.closed_kan_played_by_me(kan, self.pick_random_tile(), dora_indicator) 
		for p in player.other_players():
			p.closed_kan_played_by_other(player, kan, dora_indicator)

	def player_on_move(self, player):
		self.move_id += 1

	def is_last_round(self, winners):
		return self.potential_last and not self.players[0] in winners

	def end_of_round(self, winner, looser, wintype):
		if winner.riichi:
			ura_dora_indicators = [ self.pick_random_tile() for t in self.doras ]
			ura_doras = [ dora_from_indicator(t) for t in ura_dora_indicators ]
		else:
			ura_dora_indicators = []
			ura_doras = []

		payment, scores, minipoints  = compute_score(winner.hand, winner.sets, wintype, 
			(self.doras, ura_doras), winner.get_specials_yaku(), self.round_wind, winner.wind)
		diffs = self.payment_diffs(payment, wintype, winner, looser)


		for player in diffs:
			player.score += diffs[player]		

		looser_riichi = 0
		for player in winner.other_players():
			if player.riichi:
				looser_riichi += 1000

		winner.score += looser_riichi
		if winner.riichi:
			winner.score += 1000 # Return riichi bet

		real_diffs = {}
		for player in self.players:
			real_diffs[player] = player.score - self.original_score[player]

		logging.info("Payment: " + str(payment))
		logging.info("Scores: " + str(scores))
		logging.info("Minipoints: " + str(minipoints))
		logging.info("Ura doras: " + str(ura_doras))

		if wintype == "Tsumo":
			if payment[1][1] != 0:
				payment_name = payment[0] + " " + str(payment[1][0]) + "/" + str(payment[1][1])
			else:
				payment_name = payment[0] + " " + str(payment[1][0])
		else:
			payment_name = payment[0] + " " + str(payment[1])
			
		for player in self.players:
			player.round_end(winner, looser, wintype, payment_name, scores, minipoints, real_diffs, looser_riichi, ura_dora_indicators, self.is_last_round([winner]))

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
			player.round_end_draw(winners, loosers, diffs, self.is_last_round(winners))
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

	def roll_dice(self, dice_size):
		return self.random.randint(1,dice_size)


class DebugRound(Round):
	
	def __init__(self, players, random, round_wind, potential_last):
		def tiles(strs):
			return map(Tile, strs)

		hands = [
			[ "P5", "P5", "P2", "P2", "P4", "P4", "P6", "P7", "P8", "P1", "P1", "C4", "P1" ],
			[ "C5", "C5", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C1", "DW", "DW" ],
			[ "C5", "C5", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C1", "DG", "DG" ],
			[ "C5", "C5", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C1", "DR", "DR" ],
			[ "C9", "C5", "C8", "C5", "C5", "C5", "B5", "B5", "B5", "B5", "B1", "DW", "DW" ],
			[ "C8", "C7", "C5", "C2", "C4", "DR", "DR", "DR", "DW", "B7", "B6", "B7", "B7" ],
			[ "C8", "C9", "C5", "C6", "C4", "C2", "C3", "C1", "DW", "DW", "DW", "B7", "B7" ],
			#[ "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "C9", "DW", "DW" ],
			[ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C7", "C8" ],
			[ "DG", "DG", "DR", "C7", "C8", "DW", "DW", "DR", "B1", "B2", "B2", "B2", "B1" ],
			[ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2" ],
			[ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C9" ],
		]

		r = [ "C4", "P1", "WN", "P9", "DW", "DW", "C9", "P1","DW","DW","DW" ]
	
		self.hands = map(tiles, hands) 
		self.rnd = tiles(r)
		Round.__init__(self, players, random, round_wind, potential_last)

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
