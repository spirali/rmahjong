import graphics
import pygame
from copy import copy


class GuiManager:

	def __init__(self):
		self.widgets = []
		self.timeouts = []

	def add_widget(self, widget):
		self.widgets.append(widget)
	
	def add_widget_with_timeout(self, widget, timeout):
		self.add_widget(widget)
		self.timeouts.append((timeout + pygame.time.get_ticks(), widget))

	def remove_widget(self, widget):
		if widget in self.widgets:
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

	def tick(self):
		ticks = pygame.time.get_ticks()
		for timeout, widget in copy(self.timeouts):
			if timeout <= ticks:
				self.widgets.remove(widget)
				self.timeouts.remove((timeout, widget))


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
	
	def __init__(self, position, size, label, callback):
		Widget.__init__(self, position, size)
		self.pressed = False
		self.label = label
		self.callback = callback
		self.prepare_surface()

	def bg_surface(self):
		surface = self.create_bg_surface()
		surface.fill((0,0,0,90))
		textsurface = graphics.font.render(self.label, True, (255,255,255))
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
	
	def __init__(self, position, player_name, wind, score, direction, shout_vector):
		Widget.__init__(self, position, (200, 70))
		self.player_name = player_name
		self.score = score
		self.direction = direction
		self.selected = False
		self.wind = wind
		self.shout_vector = shout_vector
		self.update()

	def set_selection(self, value):
		self.selected = value
		self.update()

	def score_delta(self, delta):
		self.score += delta
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

		textsurface = graphics.font_small.render(self.wind.capitalize(), True, (128,128,128))
		px = surface.get_width() - textsurface.get_width()
		py = 0
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
	
	def __init__(self, score_items, total, payment, player_name, looser_riichi):
		Widget.__init__(self, (350,150), (380,400))
		self.surface = self.create_bg_surface()
		self.surface.fill((0,0,0,120))

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
		self.draw_text(yy, "Total: " + total) 
		yy += 25
		self.draw_text(yy, "Payment: " + payment) 
		if int(looser_riichi) != 0:
			yy += 25
			self.draw_text(yy, "Riichi bets from others: +" + looser_riichi) 
		
		
	def draw_text(self, y, text):
		textsurface = graphics.font.render(text, True, (255,255,255))
		self.surface.blit(textsurface, (20, y))


class RiichiStick(Widget):

	def __init__(self, position, size):
		Widget.__init__(self, position, size)
		self.surface = self.create_bg_surface()
		self.surface.fill((235,235,235,255))
		sx, sy = size
		pygame.draw.circle(self.surface, (255,40,40, 128), (sx / 2, sy / 2), min(sx, sy) / 4)


class PaymentTable(Widget):

	def __init__(self, results):
		Widget.__init__(self, (350,150), (380,400))
		self.surface = self.create_bg_surface()
		self.surface.fill((0,0,0,120))

		yy = 30
		pygame.draw.line(self.surface, (255,255,255), (0, yy), (self.size[0], yy))
		yy += 10
		for name, score, payment in results:
			self.draw_text(20, yy, name)
			yy += 20
			self.draw_text(20, yy, str(score))

			if payment < 0:
				color = (255, 0, 0)
			elif payment > 0:
				color = (0, 255, 0)
			else: 
				color = (255,255,255)	

			self.draw_text(150, yy, self.payment_prefix(payment), color = color)
			yy += 30
			pygame.draw.line(self.surface, (255,255,255), (0, yy), (self.size[0], yy))
			yy += 15

	def draw_text(self, x, y, text, color = (255,255,255)):
		textsurface = graphics.font.render(text, True, color)
		self.surface.blit(textsurface, (x, y))

	def payment_prefix(self, payment):
		if payment >= 0:
			return "+" + str(payment)
		else:
			return str(payment)

