import pygame
from pygame import display
from tilepainter import TilePainter
from directions import direction_up, direction_down, direction_left, direction_right


all_tile_names = [ "C1","C2","C3","C4","C5","C6","C7","C8","C9","B1","B2","B3","B4","B5","B6","B7","B8",
		"B9","P1","P2","P3","P4","P5","P6","P7","P8","P9","WE","WS","WW","WN","DR","DG","DW" ]

winds = [ "WE", "WS", "WW", "WN" ]


class TableTile:

	def __init__(self, table, name, position = None, direction = direction_up, callback = None):
		self.table = table
		self.name = name
		self.position = position
		self.direction = direction
		self.callback = callback
		self.highlight = False

	def remove(self):
		self.table.remove_tile(self)

	def is_vertical(self):
		return self.direction.is_vertical()

	def is_horizontal(self):
		return self.direction.is_horizontal()

	def image_id(self):
		return self.direction.dir_id

	def get_index(self):
		return all_tile_names.index(self.name)

	def on_left_button_down(self, position):
		px, py = position
		x, y = self.position
		table = self.table
		if px >= x and py >= y and px < x + table.get_face_size_x() and py < y + table.get_face_size_y():
			if self.callback:
				self.callback(self)

	def get_face_size_x(self):
		if self.direction == direction_up or self.direction_down:
			return self.table.get_face_size_x()
		else:
			return self.table.get_face_size_y()

	def get_face_size_y(self):
		if self.direction == direction_up or self.direction_down:
			return self.table.get_face_size_y()
		else:
			return self.table.get_face_size_x()

	def get_face_size(self):
		return (self.get_face_size_x(), self.get_face_size_y())

class DropZone:
	
	def __init__(self, table, initial_position, direction, row_size):
		self.position = initial_position
		self.direction = direction
		self.table = table
		self.tile_in_row = 0
		self.row_size = row_size
		self.last_tile = None
		self.last_pos = None

	def next_position(self):
		p = self.position
		self.tile_in_row += 1
		if self.tile_in_row == self.row_size:
			self.tile_in_row = 0
			self.position = self.direction.move_down(self.position, self.table.get_face_size_y() + 7)
			self.position = self.direction.move_left(self.position, self.table.get_face_size_x() * (self.row_size - 1))
		else:
			self.position = self.direction.move_right(self.position, self.table.get_face_size_x())
		return p
			
	def new_tile(self, name):
		self.last_pos = self.position
		tile = self.table.new_tile(name, self.next_position(), self.direction)
		self.last_tile = tile
		return tile

	def pop_tile(self):
		self.position = self.last_pos
		self.last_tile.remove()
	
class Table:

	def __init__(self):
		self.tp = TilePainter((640,480))
		self.reset_all()

	def reset_all(self):
		self.tiles = []
		self.hand = []
		self.doras = []

		self.open_set_positions = [ 
			((1005,690), direction_up, 0), 
			((950,80), direction_left, 0),
			((15,15), direction_down, 0),
			((45,680), direction_right, 0),
		]

		self.init_dropzones()

	def init_dropzones(self):
		dz_my = DropZone(self, (380, 470), direction_up, 6)
		dz_across = DropZone(self, (580, 140), direction_down, 6)
		dz_right = DropZone(self, (640, 410), direction_left, 6)
		dz_left = DropZone(self, (320, 210), direction_right,6)
		self.drop_zones = [ dz_my, dz_right, dz_across, dz_left ]

	def sort_hand(self):
		self.hand.sort(key=lambda t: t.get_index())

	def set_new_hand(self, tile_names):
		self.hand = [ self.new_tile(name) for name in tile_names ]
		self.arrange_hand()

	def new_tile(self, name, position = None, direction = direction_up):
		t = TableTile(self, name, position, direction)
		self.add_tile(t)
		return t

	def new_tile_to_dropzone(self, player_index, tile_name):
		return self.drop_zones[player_index].new_tile(tile_name)

	def steal_from_dropzone(self, player_index):
		self.drop_zones[player_index].pop_tile()

	def add_to_hand(self, tile):
		self.hand.append(tile)

	def arrange_hand(self):
		self.sort_hand()
		px, py = 320, 690
		for tile in self.hand:
			tile.position = (px, py)
			px += self.tp.face_size[0] + 1

	def add_tile(self, tile):
		self.tiles.append(tile)

	def remove_tile(self, tile):
		if tile in self.hand:
			self.hand.remove(tile)
		self.tiles.remove(tile)

	def remove_hand_tile(self, tile_name):
		for tile in self.hand:
			if tile.name == tile_name:
				tile.remove()
				return

	def picked_tile_position(self):
		px, py = 320 + 10, 690
		px += len(self.hand) * ( self.tp.face_size[0] + 1)
		return (px, py)

	def add_dora(self, tile_name):
		self.doras.append(self.new_tile(tile_name))
		px, py = 500, 300
		px -= self.get_face_size_x() * len(self.doras) / 2
		for tile in self.doras:
			tile.position = (px, py)
			px += self.get_face_size_x()

	def draw(self):
		self.tiles.sort(key=lambda t: t.position[0], reverse = True)
		self.tiles.sort(key=lambda t: t.position[1])
		screen = display.get_surface()
		self.tp.draw_background(screen)
		for tile in self.tiles:
			self.tp.draw_tile(screen, tile)

	def get_face_size_x(self):
		return self.tp.face_size[0]

	def get_face_size_y(self):
		return self.tp.face_size[1]

	def on_left_button_down(self, position):
		for tile in self.tiles:
			tile.on_left_button_down(position)

	def set_hand_callback(self, callback):
		for tile in self.hand:
			tile.callback = callback

	def add_open_set(self, player, tile_names, marked):
		orig_position, direction, level = self.open_set_positions[player]
		position = orig_position
		fx, fy = self.get_face_size_x(), self.get_face_size_y()
		for i, tile_name in reversed(list(enumerate(tile_names))):
			dr, mv = (direction.next, fy) if i in marked else (direction, fx)
			# Cheap hack with directions
			if direction == direction_up or direction == direction_right:
				position = direction.move_left(position, mv)
			tile = self.new_tile(tile_name, position, dr)
			if direction == direction_down or direction == direction_left:
				position = direction.move_left(position, mv)
		level += 1
		if level == 2:
			level = 0
			position = direction.move_left(orig_position, fx * 2 + fy * 2 + 10)
			position = direction.move_down(position, fy + 10)
		else:
			position = direction.move_up(orig_position, fy + 10)
		self.open_set_positions[player] = (position, direction, level)

	def find_tile_in_hand(self, tile_name):
		for tile in self.hand:
			if tile.name == tile_name:
				return tile


