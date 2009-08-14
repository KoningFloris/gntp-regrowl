import SocketServer

class GNTPServer(SocketServer.TCPServer):
	pass

class GNTPHandler(SocketServer.StreamRequestHandler):
	def handle(self):
		self.data = self.request.recv(1024)
		
		if self.data.startswith('GNTP/1.0 REGISTER'):
			print "%s sent REGISTER:" % self.client_address[0]
			GNTPRegister(self.data).send()
			self.request.send(GNTPResponse().format())
		elif self.data.startswith('GNTP/1.0 NOTIFY'):
			print "%s sent NOTIFY:" % self.client_address[0]
			GNTPNotice(self.data).send()
			self.request.send(GNTPResponse().format())
		else:
			print "%s sent UNKNOWN:" % self.client_address[0]
			print '----'
			print self.data
			print '----'
			return None
		
if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-a","--address",dest="host",help="address to listen on",default="")
	parser.add_option("-p","--port",dest="port",help="port to listen on",type="int",default=23053)
	parser.add_option("-r","--regrowl",dest='regrowl',help="ReGrowl on local machine",action="store_true",default=False)
	(options, args) = parser.parse_args()
	
	if options.regrowl:
		from local import GNTPRegister,GNTPNotice
		from gntp import GNTPResponse
	else:
		from gntp import *
	
	server = GNTPServer((options.host, options.port), GNTPHandler)
	
	sa = server.socket.getsockname()
	print "Listening for GNTP on", sa[0], "port", sa[1], "..."
	server.serve_forever()
	