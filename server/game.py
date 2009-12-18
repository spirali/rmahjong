
from tile import all_tiles, east_wind, winds, Tile
from random import Random
from eval import compute_score


class Game:

	def __init__(self, players):
		self.players = players
		self.round_id = 0

	def new_round(self):
		self.round_id += 1
		return Round(self.players)


class Round:

	def __init__(self, players):
		self.random = Random(123)
		self.init_round()
		self.init_players(players)

	def get_east_player(self):
		return self.players[0]

	def init_round(self):
		self.wall = 4 * all_tiles
		self.doras = [ self.pick_random_tile() ]
		self.round_wind = east_wind

	def init_players(self, players):
		# TODO: Random seats
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

	def get_hand(self):
		return [ self.pick_random_tile() for i in xrange(13) ]

	def get_remaining_turns(self):
		return len(self.wall) - 14

	def hidden_tiles_for_player(self, player):
		return player.left_player.hand + player.right_player.hand + player.across_player.hand + self.wall

	def end_of_round(self, winner, wintype):
		hand = winner.hand
		scores  = compute_score(hand, winner.open_sets, self.doras, False, self.round_wind, winner.wind)		
		payment = "XYZ"
		for player in self.players:
			player.round_end(winner, wintype, payment, scores)


class DebugRound(Round):
	
	def __init__(self, players):
		def tiles(strs):
			return map(Tile, strs)

		hands = [
			[ "WW", "DG", "DG", "DG", "DR", "DR", "DR", "DW", "DW", "DW", "B8", "B7", "C9" ],
			[ "C9", "C9", "C5", "C6", "C4", "C2", "C3", "C1", "DW", "DW", "DW", "B7", "B7" ],
			[ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C5", "P7" ],
			[ "DG", "DG", "DR", "DW", "DG", "DW", "DW", "DR", "B1", "B2", "B2", "B2", "B1" ],
	#		[ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2" ],
	#		[ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C9" ],
		]

		r = [ "B1", "WW", "WN", "P9", "DR", "C2", "C9" ]
	
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
