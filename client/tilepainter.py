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


from graphics import Texture, RawTexture, DisplayList
import pygame
import OpenGL.GL as gl
import OpenGL.GLU as glu


class TilePainter:

	def __init__(self, tile_size):
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
			self.tile_images[name] = img
			self.tile_textures[name] = Texture(img)

		self.tile_displaylist = display_list_of_tile(tile_size, self.back, self.border)

	def draw_tile(self, screen, position, name):
		if name != "XX":
			img = self.tile_images[name]
			w = img.get_width()
			h = img.get_height()
			screen.blit(pygame.transform.smoothscale(img, (w/4, h/4)), position)

	def draw_tile_list(self, screen, position, tile_names, space = 0):
		for i, tile_name in enumerate(tile_names):
			x = (self.face_size[0]/4 + space) * i
			self.draw_tile(screen, (x + position[0], position[1]), tile_name)


def draw_face_y(texture, m, dx, dy, normal):
	gl.glBegin(gl.GL_QUADS)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.03, 0.97)
	gl.glVertex3f(-dx, m, dy)
	texture.tex_coord(0.97, 0.97)
	gl.glVertex3f(dx, m, dy)
	texture.tex_coord(0.97, 0.03)
	gl.glVertex3f(dx, m, -dy)
	texture.tex_coord(0.03, 0.03)
	gl.glVertex3f(-dx, m, -dy)
	gl.glEnd()

def draw_face_z(texture, m, dx, dy, normal):
	gl.glBegin(gl.GL_QUADS)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.03, 0.97)
	gl.glVertex3f(dx, dy, m)
	texture.tex_coord(0.97, 0.97)
	gl.glVertex3f(dx, -dy, m)
	texture.tex_coord(0.97, 0.03)
	gl.glVertex3f(-dx,-dy, m)
	texture.tex_coord(0.03, 0.03)
	gl.glVertex3f(-dx,dy, m)
	gl.glEnd()

def draw_face_x(texture, m, dx, dy, normal):
	gl.glBegin(gl.GL_QUADS)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.03, 0.97)
	gl.glVertex3f(m, dx, dy)
	texture.tex_coord(0.97, 0.97)
	gl.glVertex3f(m, -dx, dy)
	texture.tex_coord(0.97, 0.03)
	gl.glVertex3f(m, -dx, -dy)
	texture.tex_coord(0.03, 0.03)
	gl.glVertex3f(m, dx, -dy)
	gl.glEnd()

def draw_face_xy_skew(texture, x1, x2, y1, y2, z1, z2, normal):
	gl.glBegin(gl.GL_QUADS)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.95,0.95)
	gl.glVertex3f(x1, y1, z1)
	texture.tex_coord(0.90, 0.95)
	gl.glVertex3f(x1, y1, z2)
	texture.tex_coord(0.90, 0.90)
	gl.glVertex3f(x2, y2, z2)
	texture.tex_coord(0.95, 0.90)
	gl.glVertex3f(x2, y2, z1)
	gl.glEnd()

def draw_face_yz_skew(texture, x1, x2, y1, y2, z1, z2, normal):
	gl.glBegin(gl.GL_QUADS)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.95,0.95)
	gl.glVertex3f(x1, y1, z1)
	texture.tex_coord(0.90, 0.95)
	gl.glVertex3f(x1, y2, z2)
	texture.tex_coord(0.90, 0.90)
	gl.glVertex3f(x2, y2, z2)
	texture.tex_coord(0.95, 0.90)
	gl.glVertex3f(x2, y1, z1)
	gl.glEnd()

def draw_face_xz_skew(texture, x1, x2, y1, y2, z1, z2, normal):
	gl.glBegin(gl.GL_QUADS)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.03,0.03)
	gl.glVertex3f(x1, y1, z1)
	texture.tex_coord(0.03, 0.97)
	gl.glVertex3f(x2, y1, z2)
	texture.tex_coord(0.97, 0.97)
	gl.glVertex3f(x2, y2, z2)
	texture.tex_coord(0.97, 0.03)
	gl.glVertex3f(x1, y2, z1)
	gl.glEnd()

def draw_face_triangle(texture, x1, x2, y1, y2, z1, z2, normal):
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glNormal3f(*normal)
	texture.tex_coord(0.95,0.95)
	gl.glVertex3f(x1, y1, z1)
	texture.tex_coord(0.90, 0.95)
	gl.glVertex3f(x1, y2, z2)
	texture.tex_coord(0.90, 0.90)
	gl.glVertex3f(x2, y1, z2)
	gl.glEnd()

def display_list_of_tile(tile_size, back_texture, border_texture):
	displaylist = DisplayList()
	displaylist.begin()
	x, y, z = tile_size

	dx = x - 0.08
	dy = y - 0.08
	dz = z - 0.08

	texture = back_texture
	texture.bind()

	# Back
	draw_face_y(texture, y, dx, dz, (0.0, 1.0, 0.0))

	# Back-left & back-right
	draw_face_xy_skew(texture, -x, -dx, dy, y, dz, -dz, (-1.0, 1.0, 0.0))
	draw_face_xy_skew(texture, x, dx, dy, y, dz, -dz, (1.0, 1.0, 0.0))

	# top-back & bottom-back
	draw_face_yz_skew(texture, -dx, dx, dy, y, z, dz, (0.0, 1.0, 1.0))
	draw_face_yz_skew(texture, -dx, dx, dy, y, -z, -dz, (0.0, 1.0, -1.0))

	# Left-top-back
	draw_face_triangle(texture, -dx, -x, dy, y, z, dz, (-1.0, 1.0, 1.0))
	# Right-top-back
	draw_face_triangle(texture, dx, x, dy, y, z, dz, (1.0, 1.0, 1.0))

	# Left-bottom-back
	draw_face_triangle(texture, -dx, -x, dy, y, -z, -dz, (-1.0, 1.0, -1.0))
	# Right-bottom-back
	draw_face_triangle(texture, dx, x, dy, y, -z, -dz, (1.0, 1.0, -1.0))

	texture = border_texture
	texture.bind()

	# Left & Right
	draw_face_x(texture, x, dy, dz, (1.0, 0.0, 0.0))		
	draw_face_x(texture, -x, dy, dz, (-1.0, 0.0, 0.0))		

	# Top & Bottom 
	draw_face_z(texture, z, dx + 0.04, dy + 0.05, (0.0, 0.0, 1.0))
	draw_face_z(texture, -z, dx + 0.04, dy + 0.05, (0.0, 0.0, -1.0))		
	# Don't know exactly why but with this +0.04 it looks slightly better

	# Left-front & right-front
	draw_face_xy_skew(texture, -x, -dx, -dy, -y, dz, -dz, (-1.0, -1.0, 0.0))
	draw_face_xy_skew(texture, x, dx, -dy, -y, dz, -dz, (1.0, -1.0, 0.0))

	# top-front & bottom-front
	draw_face_yz_skew(texture, -dx, dx, -dy, -y, z, dz, (0.0, -1.0, 1.0))
	draw_face_yz_skew(texture, -dx, dx, -dy, -y, -z, -dz, (0.0, -1.0, -1.0))

	# Right-top & Left-top
	draw_face_xz_skew(texture, dx, x, dy, -dy, z, dz, (1.0, 0.0, 1.0))
	draw_face_xz_skew(texture, -dx, -x, dy, -dy, z, dz, (-1.0, 0.0, 1.0))

	# Right-bottom & left-bottom
	draw_face_xz_skew(texture, dx, x, dy, -dy, -z, -dz, (1.0, 0.0, -1.0))

	displaylist.end()
	return displaylist
