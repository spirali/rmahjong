import pygame
from pygame import display, event
import array
import math
import cairo
import pygame
import rsvg


font = None

def init_fonts():
	global font
	font = pygame.font.Font("data/fonts/finalnew.ttf", 18)

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

