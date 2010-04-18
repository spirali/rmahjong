

from states import OfflineState, ConnectingState
from gui import Button, TextWidget, Label
import graphics
import pygame


class MenuState(OfflineState):

	def __init__(self, mahjong, label, items):
		OfflineState.__init__(self, mahjong)
		self.items = items
		self.label = label

	def enter_state(self):
		OfflineState.enter_state(self)
		x, y = 340, 250	
		widgets = [ TextWidget((x + 150, y), self.label, font = graphics.font_large) ]
		y += 40
		for name, callback in self.items:
			button = Button((x, y), (320, 40), name, callback)
			widgets.append(button)
			y += 50

		self.setup_widgets(widgets)

class EntryState(OfflineState):

	def __init__(self, mahjong, label, default = "", limit = 256):
		OfflineState.__init__(self, mahjong)
		self.label = label
		self.string = default
		self.limit = limit

	def enter_state(self):
		OfflineState.enter_state(self)
		x, y = 340, 250	
		l1 = Label((200, 300), (600, 40), self.label)
		self.text = Label((200, 360), (600, 40), self.string + "|")
		self.setup_widgets([l1, self.text])

	def on_key_down(self, event):
		if event.key == pygame.K_BACKSPACE:
			if self.string:
				self.string = self.string[:-1]
		elif event.key == pygame.K_RETURN:
			self.on_accept(self.string)
		elif event.key == pygame.K_ESCAPE:
			self.on_escape()
		elif len(self.string) < self.limit:
			self.string += event.unicode
		self.text.update_text(self.string + "|")

	def on_accept(self, string):
		pass

	def on_escape(self):
		pass


class PlayerNameState(EntryState):

	def __init__(self, mahjong, accept_callback):
		EntryState.__init__(self, mahjong, "Player name:", mahjong.get_username(), 18)
		self.accept_callback = accept_callback

	def on_accept(self, string):
		self.mahjong.set_username(string)
		self.accept_callback(self)

	def on_escape(self):
		self.mahjong.open_main_menu()


class AddressEntryState(EntryState):

	def __init__(self, mahjong):
		EntryState.__init__(self, mahjong, "Connect to the address:", "localhost")

	def on_accept(self, string):
		self.mahjong.set_state(ConnectingState(self.mahjong, string))

	def on_escape(self):
		self.mahjong.open_main_menu()


class PlayersCountState(MenuState):

	def __init__(self, mahjong):
		items = [ ("Singleplayer (1 human + 3 bots)", None),
					("Multiplayer (2 human + 2 bots)", None),
					("Multiplayer (3 human + 1 bot)", None),
					("Multiplayer (4 humans)", None),
					("Back to main menu", self.on_main_menu),
				]
		MenuState.__init__(self, mahjong, "Game type", items)

	def on_main_menu(self, button):
		self.mahjong.open_main_menu()


class MainMenuState(MenuState):

	def __init__(self, mahjong):
		items = [ ("New game", self.on_new_game),
					("Join to network game", self.on_join_game),
					("Options", None),
					("Quit", self.on_quit) ]
		MenuState.__init__(self, mahjong, "RMahjong", items)

	def enter_state(self):
		MenuState.enter_state(self)
		self.add_widget(TextWidget((530, 275), "v" + self.mahjong.get_version_string(), font = graphics.font_small))

	def on_new_game(self, button):
		self.mahjong.set_state(PlayersCountState(self.mahjong))

	def on_join_game(self, button):
		self.mahjong.set_state(PlayerNameState(self.mahjong, lambda state: state.mahjong.set_state(AddressEntryState(state.mahjong))))

	def on_quit(self, button):
		self.mahjong.quit()
