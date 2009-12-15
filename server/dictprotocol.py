

class DictProtocol:

	def __init__(self, connection):
		self.connection = connection
		self.buffer = {}

	def close(self):
		self.connection.close()

	def send_message(self, **kw):
		self.send_dict(kw)		

	def send_dict(self, data):
		msg_list = [ "%s|%s\n" % key_value for key_value in data.items() ]
		msg_list.append("|\n")
		self.connection.send("".join(msg_list))

	def read_message(self):
		while True:
			line = self.connection.read_line()
			if line:
				if line == "|":
					buffer = self.buffer
					self.buffer = {}
					return buffer
				key, value = line.split("|", 1)
				self.buffer[key] = value
			else:
				return None
