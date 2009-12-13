

class Tile(object):

	honor_types = [ "W", "D" ]
	suit_types = [ "P", "B", "C" ]
	
	def __init__(self, name):
		self.name = name

	def __eq__(self, x):
		return self.name == x.name
	
	def __hash__(self):
		return hash(self.name)

	def __str__(self):
		return "|%s|" % self.name

	def __repr__(self):
		return "|%s|" % self.name
	
	def __lt__(self, x):
		return self.name < x.name
	
	def __gt__(self, x):
		return self.name < x.name	

	def get_type(self):
		return self.name[0]

	def get_number(self):
		return int(self.name[1])

	def is_honor(self):
		return self.get_type() in self.honor_types
	
	def is_dragon(self):
		return self.get_type() == "D"

	def is_suit(self):
		return self.get_type() in self.suit_types

	def is_terminal(self):
		return self.is_suit() and (self.get_number() == 1 or self.get_number() == 9)

	def is_nonterminal(self):
		return self.is_suit() and self.get_number() != 1 and self.get_number() != 9

	def next_tile(self):
		n = self.get_number() + 1
		if n == 10:
			n = 1
		return Tile(self.get_type() + str(n))

	def prev_tile(self):
		n = self.get_number() - 1
		if n == 0:
			n = 9
		return Tile(self.get_type() + str(n))


red_dragon = Tile("DR")
white_dragon = Tile("DW")
green_dragon = Tile("DG")

east_wind = Tile("WE")
south_wind = Tile("WS")
west_wind = Tile("WW")
north_wind = Tile("WN")

winds = [ east_wind, south_wind, west_wind, north_wind ]
honors = [ red_dragon, white_dragon, green_dragon, east_wind, south_wind, west_wind, north_wind ]
pins = [ Tile("P1"), Tile("P2"), Tile("P3"), Tile("P4"), Tile("P5"), Tile("P6"), Tile("P7"), Tile("P8"), Tile("P9") ]
chars = [ Tile("C1"), Tile("C2"), Tile("C3"), Tile("C4"), Tile("C5"), Tile("C6"), Tile("C7"), Tile("C8"), Tile("C9") ]
bamboos = [ Tile("B1"), Tile("B2"), Tile("B3"), Tile("B4"), Tile("B5"), Tile("B6"), Tile("B7"), Tile("B8"), Tile("B9") ]
all_tiles = honors + pins + chars + bamboos


class TileSet(object):
	
	def __init__(self, closed):
		self.closed = closed
		
	def is_pon_or_kon(self):
		return False


class Pon(TileSet):
	
	def __init__(self, tile, closed = True):
		TileSet.__init__(self, closed)
		self.tile = tile
	
	def get_name(self):
		return "Pon"

	def get_tile_for_engine(self):
		return self.tile

	def tiles(self):
		return [ self.tile, self.tile, self.tile ]
	
	def is_pon_or_kon(self):
		return True
	
	def all_tiles(self, fn):
		return fn(self.tile)

	def any_tiles(self, fn):
		return fn(self.tile)

	def count_of_tile(self, tile):
		if self.tile == tile:
			return 3
		return 0

	def all_tiles_is(self, tile):
		return self.tile == tile
	
	def __repr__(self):
		return "Pon: " + str(self.tile)


class Chi(TileSet):
	
	def __init__(self, tile1, tile2, tile3, closed = True):
		TileSet.__init__(self, closed)
		self.tile1 = tile1
		self.tile2 = tile2
		self.tile3 = tile3

	def get_name(self):
		return "Chi"

	def get_tile_for_engine(self):
		return self.tile1

	def tiles(self):
		return [ self.tile1, self.tile2, self.tile3 ]

	def __repr__(self):
		return "Chi: %s %s %s" % (self.tile1, self.tile2, self.tile3)		

	def all_tiles(self, fn):
		return fn(self.tile1) and  fn(self.tile2) and fn(self.tile3)

	def any_tiles(self, fn):
		return fn(self.tile1) or fn(self.tile2) or fn(self.tile3)

	def count_of_tile(self, tile):
		if self.tile1 == tile or self.tile2 == tile or self.tile3 == tile:
			return 1
		else:
			return 0

	def all_tiles_is(self, tile):
		return False


