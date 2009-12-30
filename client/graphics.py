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
import array
import math
import cairo
import pygame
import rsvg


font = None
font_small = None

def init_fonts():
	global font, font_small
	font = pygame.font.Font("data/fonts/finalnew.ttf", 18)
	font_small = pygame.font.Font("data/fonts/finalnew.ttf", 14)

def draw_text(text, position, color):
	display.get_surface().blit(font.render(text, True, color), position)

def load_svg(filename, size = None, width = None):
	svg = rsvg.Handle(file=filename)
	dim = svg.get_dimension_data()
	if size == None:
		w = width
		h = int(w / dim[2] * dim[3])
	else:
		w, h  = size
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
	ctx = cairo.Context(surface)
	ctx.scale(w / dim[2], h / dim[3])
	svg.render_cairo(ctx)

	# FIXME: Direct creation of surface from context has invalid output
	# Dirty hack:
	surface.write_to_png("tmp.png")
	return pygame.image.load("tmp.png")

