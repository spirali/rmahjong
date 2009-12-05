import graphics
import pygame


class GuiManager:

	def __init__(self):
		self.widgets = []

	def add_widget(self, widget):
		self.widgets.append(widget)

	def remove_widget(self, widget):
		self.widgets.remove(widget)

	def draw(self, screen):
		for widget in self.widgets:
			widget.draw(screen)

	def button_up(self, button, position):
		for widget in self.widgets:
			widget.button_up(button, position)
	
	def button_down(self, button, position):
		for widget in self.widgets:
			widget.button_down(button, position)


class Widget:

	def __init__(self, position, size):
		self.position = position
		self.size = size
		self.surface = None

	def draw(self, screen):
		if self.surface:
			screen.blit(self.surface, self.position)

	def is_inside(self, position):
		px, py = position
		mx, my = self.position
		sx, sy = self.size
		return px >= mx and py >= my and px < mx + sx and py < my + sy

	def button_up(self, button, position):
		pass

	def button_down(self, button, position):
		pass

	def create_bg_surface(self):
		return pygame.Surface(self.size, pygame.SRCALPHA, pygame.display.get_surface())

	def blit_to_center(self, surface):
		px = (self.surface.get_width() - surface.get_width()) / 2
		py = (self.surface.get_height() - surface.get_height()) / 2
		self.surface.blit(surface, (px, py))

	def get_rect(self):
		return pygame.Rect( (0,0), self.size)


class Button(Widget):
	
	def __init__(self, position, size, text, callback):
		Widget.__init__(self, position, size)
		self.pressed = False
		self.text = text
		self.callback = callback
		self.prepare_surface()

	def bg_surface(self):
		surface = self.create_bg_surface()
		surface.fill((0,0,0,90))
		textsurface = graphics.font.render(self.text, True, (255,255,255))
		px = (surface.get_width() - textsurface.get_width()) / 2
		py = (surface.get_height() - textsurface.get_height()) / 2
		surface.blit(textsurface, (px, py))
		return surface

	def prepare_surface(self):
		surface = self.bg_surface()
		if not self.pressed:
			c1 = (150,150,150,90)
			c2 = (0,0,0,150)
		else:
			c1 = (0,0,0,150)
			c2 = (150,150,150,90)
		size = self.size
		pygame.draw.line(surface, c1, (0,0), (size[0], 0))
		pygame.draw.line(surface, c1, (0,0), (0,size[1]))
		pygame.draw.line(surface, c2, (size[0] - 1,0), (size[0] - 1, size[1] - 1))
		pygame.draw.line(surface, c2, (0,size[1] - 1), (size[0] - 1, size[1] - 1))
		self.surface = surface

	def button_down(self, button, position):
		if button == 1 and self.is_inside(position):
			self.pressed = True
			self.prepare_surface()

	def button_up(self, button, position):
		if self.pressed:
			self.pressed = False
			self.prepare_surface()
			self.callback(self)
	

class Label(Widget):
	
	def __init__(self, position, size, text, color = (255,255,255), bg_color = (0,0,0,90)):
		Widget.__init__(self, position, size)
		surface = pygame.Surface(size, pygame.SRCALPHA, pygame.display.get_surface())
		surface.fill(bg_color)
		textsurface = graphics.font.render(text, True, color)
		self.surface = surface
		self.blit_to_center(textsurface)


class PlayerBox(Widget):
	
	def __init__(self, position, player_name, score, direction, shout_vector):
		Widget.__init__(self, position, (200, 70))
		self.player_name = player_name
		self.score = score
		self.direction = direction
		self.selected = False
		self.shout_vector = shout_vector
		self.update()

	def set_selection(self, value):
		self.selected = value
		self.update()

	def update(self):
		surface = self.create_bg_surface()
		if self.selected:
			surface.fill((110,110,110,90))
		else:
			surface.fill((0,0,0,90))
		textsurface = graphics.font.render(self.player_name, True, (255,255,255))
		px = (surface.get_width() - textsurface.get_width()) / 2
		py = (surface.get_height() - textsurface.get_height()) / 4
		surface.blit(textsurface, (px, py))
		textsurface = graphics.font.render(str(self.score), True, (255,255,255))
		px = (surface.get_width() - textsurface.get_width()) / 2
		py = (surface.get_height() - textsurface.get_height()) / 4 * 3
		surface.blit(textsurface, (px, py))
		self.surface = pygame.transform.rotate(surface, self.direction.angle)

	def create_shoutbox(self, text):
		px = self.position[0] + self.shout_vector[0]
		py = self.position[1] + self.shout_vector[1]
		return ShoutBox((px, py), text)


class ShoutBox(Widget):
	
	def __init__(self, position, text):
		Widget.__init__(self, position, (200, 70))
		self.surface = self.create_bg_surface()
	
		rect = self.get_rect()
		pygame.draw.ellipse(self.surface, (255,255,255), rect)

		textsurface = graphics.font.render(text, True, (0,0,0))
		self.blit_to_center(textsurface)

		
class ScoreTable(Widget):
	
	def __init__(self, score_items, total_fans, payment, player_name):
		Widget.__init__(self, (350,150), (380,400))
		self.surface = self.create_bg_surface()
		self.surface.fill((0,0,0,90))

		yy = 10
		self.draw_text(yy, "Winner: " + player_name)
		yy += 15
		pygame.draw.line(self.surface, (255,255,255), (0, yy), (self.size[0], yy))
		yy += 15
		for sitem in score_items:
			self.draw_text(yy, sitem) 
			yy += 25
		pygame.draw.line(self.surface, (255,255,255), (0, yy), (self.size[0], yy))
		yy += 10
		self.draw_text(yy, "Total: " + str(total_fans)) 
		yy += 25
		self.draw_text(yy, "Payment: " + payment) 
		
	def draw_text(self, y, text):
		textsurface = graphics.font.render(text, True, (255,255,255))
		self.surface.blit(textsurface, (20, y))
