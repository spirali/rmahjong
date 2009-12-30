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

	def as_bamboo(self):
		return Tile("B" + self.name[1])

	def as_char(self):
		return Tile("C" + self.name[1])

	def as_pins(self):
		return Tile("P" + self.name[1])

	def is_bamboo(self):
		return self.name[0] == "B"

	def is_char(self):
		return self.name[0] == "C"

	def is_pins(self):
		return self.name[0] == "P"


red_dragon = Tile("DR")
white_dragon = Tile("DW")
green_dragon = Tile("DG")

east_wind = Tile("WE")
south_wind = Tile("WS")
west_wind = Tile("WW")
north_wind = Tile("WN")

dragons = [ red_dragon, white_dragon, green_dragon ]
winds = [ east_wind, south_wind, west_wind, north_wind ]
honors = [ red_dragon, white_dragon, green_dragon, east_wind, south_wind, west_wind, north_wind ]
pins = [ Tile("P1"), Tile("P2"), Tile("P3"), Tile("P4"), Tile("P5"), Tile("P6"), Tile("P7"), Tile("P8"), Tile("P9") ]
chars = [ Tile("C1"), Tile("C2"), Tile("C3"), Tile("C4"), Tile("C5"), Tile("C6"), Tile("C7"), Tile("C8"), Tile("C9") ]
bamboos = [ Tile("B1"), Tile("B2"), Tile("B3"), Tile("B4"), Tile("B5"), Tile("B6"), Tile("B7"), Tile("B8"), Tile("B9") ]
all_tiles = honors + pins + chars + bamboos

def dora_from_indicator(tile):
	if tile.is_suit():
		return tile.next_tile()
	if tile in winds:
		return winds[ (winds.index(tile) + 1) % 4 ]
	return dragons[ (dragons.index(tile) + 1) % 3 ]

class TileSet(object):
	
	def __init__(self, closed):
		self.closed = closed
		
	def is_pon_or_kan(self):
		return False

	def is_pon(self):
		return False

	def is_kan(self):
		return False

	def is_chi(self):
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
	
	def is_pon_or_kan(self):
		return True

	def is_pon(self):
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

	def __eq__(self, x):
		return isinstance(x, TileSet) and x.is_pon() and self.tile == x.tile

	def is_bamboo(self):
		return self.tile.is_bamboo()

	def is_char(self):
		return self.tile.is_char()

	def is_pins(self):
		return self.tile.is_pins()

	def as_char(self):
		return Pon(self.tile.as_char())

	def as_bamboo(self):
		return Pon(self.tile.as_bamboo())

	def as_pins(self):
		return Pon(self.tile.as_pins())


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

	def is_chi(self):
		return True

	def all_tiles_is(self, tile):
		return False

	def is_bamboo(self):
		return self.tile1.is_bamboo()

	def as_char(self):
		return Chi(self.tile1.as_char(), self.tile2.as_char(), self.tile3.as_char())

	def as_bamboo(self):
		return Chi(self.tile1.as_bamboo(), self.tile2.as_bamboo(), self.tile3.as_bamboo())

	def as_pins(self):
		return Chi(self.tile1.as_pins(), self.tile2.as_pins(), self.tile3.as_pins())

	def __eq__(self, x):
		return isinstance(x, TileSet) and x.is_chi() and self.tile1 == x.tile1
