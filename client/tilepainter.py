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


from graphics import load_svg, Texture, RawTexture
import pygame

class TilePainter:

	def __init__(self, screen_size):
		width = 450 * 4
		self.image = pygame.image.load("data/tiles/default.png")
		self.bg_image = pygame.image.load("data/bg/default.png")

		self.border = Texture(pygame.image.load("data/tiles/border.png"))
		self.back = Texture(pygame.image.load("data/tiles/back.png"))
	
		scale = width / 768.0
		self.face_size = (68.0 * scale, 82.0 * scale)
		self.matrix_size = (69.0 * scale, 88.5 * scale)
		self.matrix_start = (1 * scale, 120.5 * scale)

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
		self.tile_textures = {}
		for name,source in tile_sources.items():
			tx, ty = source
			tx = tx * self.matrix_size[0] + self.matrix_start[0]
			ty = ty * self.matrix_size[1] + self.matrix_start[1]
			img = self.image.subsurface(pygame.Rect((tx, ty), self.face_size))
			self.tile_textures[name] = Texture(img)


