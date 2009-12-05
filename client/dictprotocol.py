

class DictProtocol:

	def __init__(self, connection):
		self.connection = connection
		self.buffer = {}

	def close(self):
		self.connection.close()

	def send_message(self, **kw):
		self.send_dict(kw)		

	def send_dict(self, data):
		for key_value in data.items():
			self.connection.send("%s|%s\n" % key_value)
		self.connection.send("|\n")
	
	def read_message(self):
		line = self.connection.read_line()
		if line:
			if line == "|":
				buffer = self.buffer
				self.buffer = {}
				return buffer
			key, value = line.split("|", 1)
			self.buffer[key] = value
		return None
