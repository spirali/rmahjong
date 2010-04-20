

from states import OfflineState, ConnectingState, StartServerState
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
		items = [ ("Singleplayer (1 human + 3 bots)", self.on_run1),
					("Multiplayer (2 human + 2 bots)", self.on_run2),
					("Multiplayer (3 human + 1 bot)", self.on_run3),
					("Multiplayer (4 humans)", self.on_run4),
					("Back to main menu", self.on_main_menu),
				]
		MenuState.__init__(self, mahjong, "Game type", items)

	def on_main_menu(self, button):
		self.mahjong.open_main_menu()

	def on_run1(self, button):
		self.run_server(1)

	def on_run2(self, button):
		self.run_server(2)

	def on_run3(self, button):
		self.run_server(3)

	def on_run4(self, button):
		self.run_server(4)

	def run_server(self, number_of_players):
		self.mahjong.set_state(StartServerState(self.mahjong, number_of_players))


class MainMenuState(MenuState):

	def __init__(self, mahjong):
		items = [ ("New game", self.on_new_game),
					("Join to network game", self.on_join_game),
					("Options", self.on_options),
					("Quit", self.on_quit) ]
		MenuState.__init__(self, mahjong, "RMahjong", items)

	def enter_state(self):
		MenuState.enter_state(self)
		self.add_widget(TextWidget((530, 275), "v" + self.mahjong.get_version_string(), font = graphics.font_small))

	def on_new_game(self, button):
		self.mahjong.set_state(PlayerNameState(self.mahjong, lambda state: state.mahjong.set_state(PlayersCountState(state.mahjong))))

	def on_join_game(self, button):
		self.mahjong.set_state(PlayerNameState(self.mahjong, lambda state: state.mahjong.set_state(AddressEntryState(state.mahjong))))

	def on_quit(self, button):
		self.mahjong.quit()

	def on_options(self, button):
		self.mahjong.set_state(OptionsState(self.mahjong))


class OptionsState(MenuState):

	def __init__(self, mahjong):
		items = [ ("Toggle fullscreen", self.on_fullscreen),
					("Back to main menu", self.on_back) ]
		MenuState.__init__(self, mahjong, "Options", items)

	def on_back(self, button):
		self.mahjong.open_main_menu()

	def on_fullscreen(self, button):
		self.mahjong.toggle_fullscreen()
