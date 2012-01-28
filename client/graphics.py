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
from pygame import display, event
import pygame
import locale
import OpenGL.GL as gl
import OpenGL.GLU as glu

font = None
font_small = None
font_large = None


def init_fonts():
	global font, font_small, font_large
	if locale.getdefaultlocale()[0].startswith("fr"):
		# We need a font with french special letters
		font_name = "data/fonts/DejaVuSerif.ttf"
	else:
		font_name = "data/fonts/finalnew.ttf"
	font = pygame.font.Font(font_name, 18)
	font_small = pygame.font.Font(font_name, 14)
	font_large = pygame.font.Font(font_name, 32)

def setup_perspective():
	glu.gluPerspective(30, 1.0*1024/768, 0.1, 200.0)

def init_opengl(width, height):
	gl.glEnable(gl.GL_TEXTURE_2D)
	gl.glShadeModel(gl.GL_SMOOTH)
	gl.glClearColor(0.0, 0.0, 0.0, 0.0)
	gl.glClearDepth(1.0)
	gl.glEnable(gl.GL_DEPTH_TEST)
	gl.glDepthFunc(gl.GL_LEQUAL)
	gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
	gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)

	gl.glViewport(0, 0, width, height)
	gl.glMatrixMode(gl.GL_PROJECTION)
	gl.glLoadIdentity()
	setup_perspective()
	gl.glMatrixMode(gl.GL_MODELVIEW)
	gl.glLoadIdentity()

	gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, (1.0,1.0,1.0, 1.0));
	gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, (1.0,1.0,1.0,1.0));
	gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, (1.0,1.0,1.0,1.0));

	gl.glLightfv(gl.GL_LIGHT1, gl.GL_DIFFUSE, (0.7,0.7,0.7, 0.7));
	gl.glLightfv(gl.GL_LIGHT1, gl.GL_AMBIENT, (0.0,0.0,0.0,0.0));
	gl.glLightfv(gl.GL_LIGHT1, gl.GL_SPECULAR, (1.0,1.0,1.0,0.5));

	gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, (1.0,1.0,1.0,1.0));
	gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_EMISSION, (0.0,0.0,0.0,1.0));
	gl.glMateriali(gl.GL_FRONT_AND_BACK, gl.GL_SHININESS, 50);

	gl.glEnable(gl.GL_LIGHT0);
	gl.glEnable(gl.GL_LIGHT1);
	gl.glEnable(gl.GL_LIGHTING);

	gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA);
	gl.glDisable(gl.GL_ALPHA_TEST)

def draw_text(text, position, color):
	display.get_surface().blit(font.render(text, True, color), position)

def blit_to_center(dest_surface, surface):
	px = (dest_surface.get_width() - surface.get_width()) / 2
	py = (dest_surface.get_height() - surface.get_height()) / 2
	dest_surface.blit(surface, (px, py))

def enable2d():
	#v = gl.glGetIntegerv(gl.GL_VIEWPORT)
	gl.glMatrixMode(gl.GL_PROJECTION)
	gl.glPushMatrix()
	gl.glLoadIdentity()
	#gl.glOrtho(0, v[2], 0, v[3], -1, 1)
	gl.glOrtho(0, 1024, 0, 768, -1, 1)
	gl.glMatrixMode(gl.GL_MODELVIEW)
	gl.glPushMatrix()
	gl.glLoadIdentity()
	gl.glDisable(gl.GL_DEPTH_TEST)
	gl.glEnable(gl.GL_BLEND)
	gl.glDisable(gl.GL_LIGHTING);

def disable2d():
	gl.glMatrixMode(gl.GL_PROJECTION)
	gl.glPopMatrix()
	gl.glMatrixMode(gl.GL_MODELVIEW)
	gl.glPopMatrix()
	gl.glEnable(gl.GL_DEPTH_TEST)
	gl.glDisable(gl.GL_BLEND)
	gl.glEnable(gl.GL_LIGHTING);

class DisplayList:

	def __init__(self):
		self.index = gl.glGenLists(1)

	def call(self):
		gl.glCallList(self.index)

	def free(self):
		gl.glDeleteLists([self.index])

	def begin(self):
		gl.glNewList(self.index, gl.GL_COMPILE)

	def end(self):
		gl.glEndList()

class RawTexture:

	def __init__(self, surface):
		self.texture, self.width, self.height = self._from_surface(surface)

	def bind(self):
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

	def free(self):
		gl.glDeleteTextures([self.texture])

	def draw(self, x, y, scale_x = 1.0, scale_y = 1.0):
		y = 768 - y
		self.bind()
		gl.glBegin(gl.GL_QUADS)
		gl.glColor4f(1.0, 1.0, 1.0, 1.0)
		self.tex_coord(0.0,1.0)
		gl.glVertex2f(x, y)
		self.tex_coord(1.0,1.0)
		gl.glVertex2f(x + self.width * scale_x, y)
		self.tex_coord(1.0,0.0)
		gl.glVertex2f(x + self.width * scale_x, y - self.height * scale_y)
		self.tex_coord(0.0,0.0)
		gl.glVertex2f(x, y - self.height * scale_y)
		gl.glEnd()

	def _from_surface(self, surface):
		data = pygame.image.tostring(surface, "RGBA", 1)
		width = surface.get_width()
		height = surface.get_height()
		texture = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
		gl.glTexEnvf( gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE );
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_ANISOTROPY_EXT, 1000.0)

		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)
		glu.gluBuild2DMipmaps(gl.GL_TEXTURE_2D, 4, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data );
		return texture, width, height

	def tex_coord(self, x, y):
		gl.glTexCoord2f(x, y)


def find_texture_size(size):
	x = 8
	while x < size:
		x *= 2
	return x


class Texture(RawTexture):

	def __init__(self, surface):
		w = surface.get_width()
		h = surface.get_height()
		new_size = max(find_texture_size(w), find_texture_size(h))
		new_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
		new_surface.blit(surface, (0,new_size - h))

		self.texture, _w, _h = self._from_surface(new_surface)
		self.width = w
		self.height = h

		self.x_coef = float(w) / new_size
		self.y_coef = float(h) / new_size

	def tex_coord(self, x, y):
		gl.glTexCoord2f(self.x_coef * x, self.y_coef * y)
