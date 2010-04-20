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

class TilePainter:

	def __init__(self, screen_size):
		width = 450
	#	self.image = load_svg("data/default.svgz", width = width)
	#	self.bg_image = load_svg("data/bg/default.svg", width = 50)
		self.image = pygame.image.load("data/tiles/default.png")
		self.bg_image = pygame.image.load("data/bg/default.png")
		scale = width / 768.0
		self.face_size = (68.0 * scale, 82.0 * scale)
		self.matrix_size = (69.0 * scale, 88.5 * scale)

		self.tile_size = [ (97.0 * scale, 115.0 * scale), (116.0 * scale, 97.0 * scale), (97.0 * scale, 115.0 * scale)]
		self.tile_start = [ (0,0), (195.0 * scale,0), (97.5 * scale,0), (195.0 * scale,0) ]

		self.matrix_start = (1 * scale, 120.5 * scale)
		self.face_offset = [ (28.0 * scale, 3.0 * scale),  (30.0 * scale, 0.0 * scale) ]
		self.face_offset.append(self.face_offset[0])

		tile_sources = {}
		tile_sources["C1"] = (0,0)
		tile_sources["C2"] = (1,0)
		tile_sources["C3"] = (2,0)
		tile_sources["C4"] = (3,0)
		tile_sources["C5"] = (4,0)
		tile_sources["C6"] = (5,0)
		tile_sources["C7"] = (6,0)
		tile_sources["C8"] = (7,0)
		tile_sources["C9"] = (8,0)
		tile_sources["B1"] = (0,1)
		tile_sources["B2"] = (1,1)
		tile_sources["B3"] = (2,1)
		tile_sources["B4"] = (3,1)
		tile_sources["B5"] = (4,1)
		tile_sources["B6"] = (5,1)
		tile_sources["B7"] = (6,1)
		tile_sources["B8"] = (7,1)
		tile_sources["B9"] = (8,1)
		tile_sources["P1"] = (0,2)
		tile_sources["P2"] = (1,2)
		tile_sources["P3"] = (2,2)
		tile_sources["P4"] = (3,2)
		tile_sources["P5"] = (4,2)
		tile_sources["P6"] = (5,2)
		tile_sources["P7"] = (6,2)
		tile_sources["P8"] = (7,2)
		tile_sources["P9"] = (8,2)
		tile_sources["WE"] = (6,3)
		tile_sources["WS"] = (5,3)
		tile_sources["WW"] = (7,3)
		tile_sources["WN"] = (4,3)
		tile_sources["DR"] = (2,4)
		tile_sources["DG"] = (1,4)
		tile_sources["DW"] = (0,4)

		self.tile_images = {}
		for name,source in tile_sources.items():
			tx, ty = source
			tx = tx * self.matrix_size[0] + self.matrix_start[0]
			ty = ty * self.matrix_size[1] + self.matrix_start[1]
			img = self.image.subsurface(pygame.Rect((tx, ty), self.face_size))
			self.tile_images[name] = [img]
			self.tile_images[name].append(pygame.transform.rotate(img, 270))
			self.tile_images[name].append(pygame.transform.rotate(img, 180))
			self.tile_images[name].append(pygame.transform.rotate(img, 90))

	def draw_background(self, screen):
		w = self.bg_image.get_width()
		h = self.bg_image.get_height()
		for y in xrange(0, screen.get_height(), h):
			for x in xrange(0, screen.get_width(), w):
				screen.blit(self.bg_image, (x, y))

	def draw_tile(self, screen, tile):
		if tile.is_vertical():
			if tile.highlight:
				bg_id = 2
			else:
				bg_id = 0
		else:
			bg_id = 1
		self._draw_tile(screen, tile.position, self.tile_images[tile.name][tile.image_id()], bg_id)

	def _draw_tile(self, screen, position, img, bg_id):
		px = position[0] - self.face_offset[bg_id][0]
		py = position[1] - self.face_offset[bg_id][1]
		screen.blit(self.image, (px, py), pygame.Rect(self.tile_start[bg_id], self.tile_size[bg_id]))	
		screen.blit(img, position)	
