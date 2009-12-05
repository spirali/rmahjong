
import socket
import select
import string

class ConnectionClosed(Exception):
	pass


class Connection:
	def __init__(self, sock = None):
		if sock == None:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket = sock

	def connect(self, addr, port):
		return self.socket.connect_ex((addr, port)) == 0
	
	def bind_and_listen(self, port, reuse_addr = False):
		if reuse_addr:
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(('0.0.0.0', port))
		self.socket.listen(5)

	def is_read_ready(self):
		return len(select.select([self.socket], [], [], 0)[0]) > 0

	def wait_for_read(self, timeout = None):
		return len(select.select([self.socket], [], [], timeout)[0]) > 0
	
	def accept(self):
		if self.is_read_ready():
			return Connection(self.socket.accept()[0])
		else:
			return None

	def close(self):
		self.socket.close()

	def read_line(self):
		# TODO: Handle long lines
		try:
			if self.is_read_ready():
				buf = []
				while True:
					char = self.socket.recv(1)
					if char == '\n':
						return string.join(buf,'')
					if char == '':
						raise ConnectionClosed()
					buf.append(char)
		except socket.error,e:
			raise ConnectionClosed()

	def send(self, string):
		try:
			self.socket.send(string)
		except socket.error,e:
			raise ConnectionClosed()	

	def get_peer_name(self):
		return self.socket.getpeername()[0]

	def get_peer_port(self):
		return self.socket.getpeername()[1]
