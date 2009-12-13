
from subprocess import PIPE, Popen
from threading import Thread, Lock
from Queue import Queue
from tile import Tile

BOT_PATH = "../bot/bot"


class BotEngineException(Exception):
	pass


class BotEngine(Thread):

	def __init__(self):
		Thread.__init__(self)
		self.queue = Queue(2)
		self.process = Popen([ BOT_PATH ], bufsize = 0, stdin = PIPE, stdout = PIPE)
		self.nonblocking = True
		self.process_out = self.process.stdout
		self.process_in = self.process.stdin
		self.thread_quit = False
		self.start()

	def run(self):
		while not self.thread_quit:
			line = self.process_out.readline()
			self.queue.put(line, True)

	def shutdown(self):
		self.thread_quit = True
		self._write("QUIT\n")

	def get_tile(self):
		if self._is_next_line():
			return Tile(self._read_line().strip())
		else:
			return None

	def set_blocking(self):
		self.nonblocking = False
	
	def set_hand(self, tiles):
		self._write("HAND\n")	
		self._set_tiles(tiles)

	def set_turns(self, turns):
		self._write("TURNS\n%d\n" % turns)

	def set_wall(self, tiles):
		self._write("WALL\n")	
		self._set_tiles(tiles)

	def set_sets(self, sets):
		self._write("SETS\n")
		for set in sets:
			self._write("%s %s " % (set.get_name(), set.get_tile_for_engine().name))
		self._write("\n")

	def question_discard(self):
		self._write("DISCARD\n")

	def _write(self, string):
		self.process_in.write(string)

	def _set_tiles(self, tiles):
		message = " ".join((tile.name for tile in tiles))
		self._write(message + "\n")

	def _read_line(self):
		line = self.queue.get()
		if line[:5] == "Error":
			raise BotEngineException(line)
		return line

	def _is_next_line(self):
		return not self.queue.empty() or not self.nonblocking
