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


import pygame
from pygame import display
import OpenGL.GL as gl
import OpenGL.GLU as glu
from tilepainter import TilePainter
from tilepainter import draw_face_x, draw_face_y, draw_face_z, draw_face_triangle
from tilepainter import draw_face_xy_skew, draw_face_xz_skew, draw_face_yz_skew
from directions import direction_up, direction_down, direction_left, direction_right
from graphics import Texture, RawTexture, setup_perspective
import utils

all_tile_names = [ "C1","C2","C3","C4","C5","C6","C7","C8","C9","B1","B2","B3","B4","B5","B6","B7","B8",
		"B9","P1","P2","P3","P4","P5","P6","P7","P8","P9","WE","WS","WW","WN","DR","DG","DW" ]

winds = [ "WE", "WS", "WW", "WN" ]

tile_size = (1.0, 0.60, 1.33)


class Tile:

	def __init__(self, table, name, position = None, rotation = (0.0, 0.0)):
		self.table = table
		self.name = name
		self.position = position
		self.rotation = rotation
		self.callback = None
		self.visible = True

	def get_index(self):
		return all_tile_names.index(self.name)

	def remove(self):
		self.table.remove_tile(self)

	def on_left_button_down(self):
		if self.callback:
			self.callback(self)

	def hide(self):
		self.visible = False

	def show(self):
		self.visible = True

	def is_visible(self):
		return self.visible

	def draw(self):
		if not self.visible:
			return

		gl.glPushMatrix()
		gl.glTranslatef(self.position[0], self.position[1], self.position[2] + 1.33)
		gl.glRotate(self.rotation[0],0.0, 0.0, 1.0)
		gl.glRotate(self.rotation[1],1.0, 0.0, 0.0)

		#x = 10.4
		#gl.glScale(x,x, x)

		self._render()
		gl.glPopMatrix()

	def _render(self):
		x, y, z = tile_size

		dx = x - 0.08
		dy = y - 0.08
		dz = z - 0.08

		if self.name != "XX":
			texture = self.table.tp.tile_textures[self.name]
			texture.bind()
			# Front
			draw_face_y(texture, -y, dx,  dz, (0.0, -1.0, 0.0))
		self.table.tp.tile_displaylist.call()

	def __repr__(self):
		return "<Tile %s>" % self.name


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
		self.last_pos = p
		self.tile_in_row += 1
		if self.tile_in_row == self.row_size:
			self.tile_in_row = 0
			self.position = self.direction.move_down(self.position, self.table.get_face_size_y() + 0.2)
			self.position = self.direction.move_left(self.position, self.table.get_face_size_x() * (self.row_size - 1))
		else:
			self.position = self.direction.move_right(self.position, self.table.get_face_size_x())
		return p
			
	def new_tile(self, name):
		pos = self.next_position()
		tile = self.table.new_tile(name, (pos[0], pos[1], 0) , (self.direction.angle, -90))
		self.last_tile = tile
		return tile

	def pop_tile(self):
		self.tile_in_row = (self.tile_in_row - 1) % self.row_size
		self.position = self.last_pos
		self.last_tile.remove()


class RiichiStick:

	def __init__(self, position, rotation, texture):
		self.position = position
		self.rotation = rotation
		self.texture = texture
		self.size = (3.6, 0.25, 0.2)
		self.visible = False

	def hide(self):
		self.visible = False

	def show(self):
		self.visible = True

	def draw(self):
		if not self.visible:
			return
		sx, sy, sz = self.size
		gl.glPushMatrix()
		gl.glTranslatef(self.position[0], self.position[1], self.position[2] + sz)
		gl.glRotate(self.rotation,0.0, 0.0, 1.0)
		
		texture = self.texture
		texture.bind()

		gl.glBegin(gl.GL_QUADS)
		gl.glNormal3f(0.0,0.0, 1.0)
		texture.tex_coord(0.0,0.0)
		gl.glVertex3f(-sx,-sy, sz)
		texture.tex_coord(0.0, 1.0)
		gl.glVertex3f(-sx,sy, sz)
		texture.tex_coord(1.0, 1.0)
		gl.glVertex3f(sx,sy, sz)
		texture.tex_coord(1.0, 0.0)
		gl.glVertex3f(sx,-sy, sz)
		gl.glEnd()

		#TODO: Other faces
	
		gl.glPopMatrix()


class OpenSetPlace:
	
	"""
		tile_source 
			= 0 - from right player
			= 1 - from middle player
			= 2 - form left player
	"""

	def __init__(self, table, init_pos, direction):
		self.table = table
		fx, fy = 2, 2.66 + 1.3
		p2 = direction.move_left(init_pos, fx * 4.7)
		self.positions = [
			init_pos, 
			direction.move_down(init_pos, fy),
			p2,
			direction.move_down(p2, fy),
		]

		self.sets = []
		self.direction = direction

	def new_set(self, tile_names, tile_source):
		i = len(self.sets)
		pos = self.positions[i]

		tiles = []
		for j, tile_name in enumerate(tile_names):
			if self._marked(j, tile_source, tile_names):
				d = self.direction.next
				m = 2.3
				pos = self.direction.move_left(pos, 0.3)
			else:
				d = self.direction
				m = 2.0
			
			if tile_name == "XX":
				tiles.append(self.table.new_tile(tile_name, pos, (d.angle, -270)))
			else:
				tiles.append(self.table.new_tile(tile_name, pos, (d.angle, -90)))

			pos = self.direction.move_left(pos, m)
		self.sets.append((tiles, tile_source))

	def add_extra_kan_tile(self, openset_id, tile_name):
		tiles, tile_source = self.sets[openset_id]
		assert len(tiles) == 3 and tile_source != -1
		tile = tiles[tile_source]
		tile.position = self.direction.move_down(tile.position, 1.0)
		pos = self.direction.move_up(tile.position, 2.0)
		self.table.new_tile(tile_name, pos, tile.rotation)

	def _marked(self, tile_pos, tile_source, tiles):
		if len(tiles) == 3:
			return tile_pos == tile_source
		else:
			if tile_source == 0:
				return tile_pos == 0
			elif tile_source == 1:
				return tile_pos == 1 or tile_pos == 2
			elif tile_source == 2:
				return tile_pos == 3
			
	def find_set_id(self, tile_names):
		for i, (tiles, tile_source) in enumerate(self.sets):
			if [ t.name for t in tiles ] == tile_names:
				return i
		return None


class Table:

	def __init__(self):
		self.tp = TilePainter(tile_size)
		
		# FIXME
		self.bg_texture = RawTexture(self.tp.bg_image)

		self.rstick_texture = RawTexture(pygame.image.load("data/others/rstick.png"))
		self.riichi_sticks = [
			RiichiStick( (-0.9,4,0), 0, self.rstick_texture),
			RiichiStick( (3.4,8.1,0), 90, self.rstick_texture),
			RiichiStick( (-0.8,12,0), 0, self.rstick_texture),
			RiichiStick( (-5.0,8.1,0), 90, self.rstick_texture),
		]

		self.reset_all()

	def reset_all(self):

		for stick in self.riichi_sticks:
			stick.hide()

		self.tiles = []
		self.hand = []
		self.dora_indicators = []
		self.ura_dora_indicators = []

		self.set_places = [ OpenSetPlace(self, init_pos, direction) for init_pos, direction in
			[ 
			((17.7,-13.5,0), direction_up), 
			((22,26.5,0), direction_left),
			((-15,34,0), direction_down),
			((-23.1,-6.0,0), direction_right),
			]]

		self.init_dropzones()

		self.init_wall()
		self.other_hands = []

	def init_wall(self):
		wall = []

		for x in xrange(17):
			wall.append(self.new_dummy_tile(((16-x)*2 - 17, -10, 1.22), (180,90)))
			wall.append(self.new_dummy_tile(((16-x)*2 - 17, -10, 0), (180,90)))

		for x in xrange(17):
			wall.append(self.new_dummy_tile((-19, x*2 -7, 1.22), (-90,90)))
			wall.append(self.new_dummy_tile((-19, x*2 -7, 0), (-90,90)))

		for x in xrange(17):
			wall.append(self.new_dummy_tile((x*2 - 17, 28, 1.22), (180,90)))
			wall.append(self.new_dummy_tile((x*2 - 17, 28, 0), (180,90)))

		for x in xrange(17):
			wall.append(self.new_dummy_tile((17.5, (16-x)*2 -7 , 1.22), (90,90)))
			wall.append(self.new_dummy_tile((17.5, (16-x)*2 -7 , 0), (90,90)))
		self.wall = wall

	def break_wall(self, dice_num):
		w = utils.right_shift_list(self.wall, (dice_num % 4) * 34)
		w = utils.left_shift_list(w, dice_num * 2)

		for tile in w[:4 * 13]:
			tile.remove()
		del w[:4 * 13]
		self.wall = w

		o1, o2, o3 = [], [], []

		for x in xrange(13):
			o1.append(self.new_other_hand_tile(1, x))
			o2.append(self.new_other_hand_tile(2, x))
			o3.append(self.new_other_hand_tile(3, x))

		self.other_hands = [ o1, o2, o3 ]

	def picked_other_hand_tile(self, player_id):
		ln = len(self.other_hands[player_id - 1])
		return self.new_other_hand_tile(player_id, ln + 0.3)

	def new_other_hand_tile(self, player_id, x):
		if player_id == 1:
			return self.new_dummy_tile((22.5, x * 2.08 - 4, 0), (90, 0))
		if player_id == 3:
			return self.new_dummy_tile((-24.5, (14-x) * 2.08 - 3, 0), (-90, 0))
		if player_id == 2:
			return self.new_dummy_tile(((14-x) * 2.08 - 14, 36, 0), (180, 0))

	def remove_tiles_from_other_hand(self, player_id, count):
		for tile in self.other_hands[player_id-1][-count:]:
			tile.remove()
		del self.other_hands[player_id-1][-count:]

	def remove_tile_from_wall(self):
		self.wall[0].remove()
		del self.wall[0]

	def init_dropzones(self):
		dz_my = DropZone(self, (-6, 0), direction_up, 6)
		dz_across = DropZone(self, (4, 15), direction_down, 6)
		dz_right = DropZone(self, (6.5, 2.5), direction_left, 6)
		dz_left = DropZone(self, (-8.5, 12.5), direction_right,6)
		self.drop_zones = [ dz_my, dz_right, dz_across, dz_left ]

	def sort_hand(self):
		self.hand.sort(key=lambda t: t.get_index())

	def set_new_hand(self, tile_names):
		self.hand = [ self.new_tile(name) for name in tile_names ]
		self.arrange_hand()

	def new_dummy_tile(self, position, rotation):
		return self.new_tile("XX", position, rotation)

	def new_tile(self, name, position = None, rotation = (0,0)):
		t = Tile(self, name, position, rotation)
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
		px, py = -11.5, -15
		for tile in self.hand:
			tile.position = (px, py, 0)
			tile.rotation = (0.0, -25.0)
			px += 2.08

	def picked_tile(self, tile_name):
		px, py = -11.5, -15
		px += len(self.hand) * 2.08 + 0.5
		return self.new_tile(tile_name, (px, py, 0), (0.0, -25.0))

	def add_tile(self, tile):
		self.tiles.append(tile)

	def remove_tile(self, tile):
		if tile in self.hand:
			self.hand.remove(tile)
		self.tiles.remove(tile)

	def remove_dead_wall_tile_for_kan(self):
		for tile in [ self.wall[-2], self.wall[-1], self.wall[-4], self.wall[-3] ]:
			if tile.is_visible():
				tile.hide()
				return

	def remove_hand_tile_by_name(self, tile_name):
		for tile in self.hand:
			if tile.name == tile_name:
				tile.remove()
				return
		raise Exception("Tile is not in hand")

	def add_dora_indicator(self, tile_name):
		pos = len(self.dora_indicators)
		dorai = self.wall[-(pos * 2 + 6)]
		self.dora_indicators.append(dorai)
		dorai.rotation = (dorai.rotation[0], -90)
		dorai.name = tile_name

	def add_ura_dora_indicator(self, tile_name):
		pass

	def draw(self):
		gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
		self._draw_init()
		self._draw_background()

		for stick in self.riichi_sticks:
			stick.draw()

		for tile in self.tiles:
			tile.draw()

	def _draw_init(self):
		gl.glLoadIdentity()
		#gl.glTranslatef(1.0, -3.5, -50.0)
		#gl.glRotatef(-45.0, 1.0, 0.0, 0.0)

	#	gl.glTranslatef(2.0, -3.5, -51.0)
	#	gl.glRotatef(-45.0, 1.0, 0.0, 0.0)
		gl.glTranslatef(2.0, -3.5, -76.0)
		gl.glRotatef(-45.0, 1.0, 0.0, 0.0)


	#	gl.glTranslatef(1.0, -3.5, -55.0)
	#	gl.glRotatef(-55.0, 1.0, 0.0, 0.0)


	#	gl.glTranslatef(0.0, -7.0, -65.0)
	#	gl.glRotatef(-05.0, 1.0, 0.0, 0.0)

		gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, (-5.0,5.0,30.0,1.0));
		gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, (-5.0,-20.0,30.0,1.0));

	def _draw_background(self):
		gl.glColor3f(1.0, 1.0, 1.0)
		texture = self.bg_texture
		texture.bind()
		gl.glBegin(gl.GL_QUADS)
		gl.glNormal3f(0.0,0.0, 1.0)
		tx = 60
		texture.tex_coord(0, tx)
		gl.glVertex3f(-100.0, 100.0, 0)
		texture.tex_coord(tx, 0)
		gl.glVertex3f(100.0, 100.0, 0)
		texture.tex_coord(tx, tx)
		gl.glVertex3f(100.0, -100.0, 0)
		texture.tex_coord(0.0, 0.0)
		gl.glVertex3f(-100.0, -100.0, 0)
		gl.glEnd()

	def get_face_size_x(self):
		return 2.0

	def get_face_size_y(self):
		return 2.66

	def pick_object_on_position(self, position):
		v = gl.glGetIntegerv(gl.GL_VIEWPORT)
		gl.glSelectBuffer(len(self.tiles) * 20)
		gl.glRenderMode(gl.GL_SELECT)
		gl.glInitNames()
		self._draw_init()
		gl.glPushName(-1)

		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glPushMatrix()
		gl.glLoadIdentity()
		glu.gluPickMatrix(position[0], v[3] - position[1], 2.0, 2.0, v);

		setup_perspective()

		gl.glMatrixMode(gl.GL_MODELVIEW)

		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		self._draw_init()


		for tile_id, tile in enumerate(self.tiles):
			gl.glLoadName(tile_id)
			tile.draw()
		pygame.display.flip()


		gl.glFlush()
		hits = gl.glRenderMode(gl.GL_RENDER)
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glPopMatrix()
		gl.glMatrixMode(gl.GL_MODELVIEW)

		if hits:
			hits.sort(key = lambda s: s.near)
			tile_id = hits[0].names[0]
			return self.tiles[tile_id]
		return None

	def on_left_button_down(self, position):
		tile = self.pick_object_on_position(position)
		if tile:
			tile.on_left_button_down()

	def set_hand_callback(self, callback):
		for tile in self.hand:
			tile.callback = callback

	def find_open_set_id(self, player_id, tile_names):
		place = self.set_places[player_id]
		return place.find_set_id(tile_names)

	def add_open_set(self, player_id, tile_names, stolen_from):
		if stolen_from == -1:
			tile_source = -1
		else:
			table = {
				0: [ -1, 0, 1, 2 ],
				1: [ 2, -1, 0, 1 ],
				2: [ 1, 2, -1, 0 ],
				3: [ 0, 1, 2, -1 ],
			}
			tile_source = table[player_id][stolen_from]
		place = self.set_places[player_id]
		place.new_set(tile_names, tile_source)

	def add_extra_kan_tile(self, player_id, openset_id, tile_name):
		place = self.set_places[player_id]
		place.add_extra_kan_tile(openset_id, tile_name)

	def find_tile_in_hand(self, tile_name):
		for tile in self.hand:
			if tile.name == tile_name:
				return tile

	def set_riichi(self, player_id):
		self.riichi_sticks[player_id].show()
