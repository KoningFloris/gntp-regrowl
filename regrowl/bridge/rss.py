"""
Create a RSS feed from all the received growl messages

Config Example:
[regrowl.bridge.rss]
maxitems = 100
"""

from __future__ import absolute_import

import logging
import sys
import os
import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import datetime
import PyRSS2Gen as PyRSS2Gen
import time

from regrowl.regrowler import ReGrowler

logger = logging.getLogger(__name__)

__all__ = ['RssNotifier']

SPACER = '=' * 80
packetList = list()

proID2 = os.fork()#create a seperate for the simplehttpserver to serve the index.html (which contains the rss xml)
if proID2 == 0:
	ServerClass  = BaseHTTPServer.HTTPServer	
	port = 8000
	server_address = ('0.0.0.0', port)	
	httpd = ServerClass(server_address, SimpleHTTPServer.SimpleHTTPRequestHandler)
	sa = httpd.socket.getsockname()
	print "Serving RSS on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()			

class RssNotifier(ReGrowler):
    valid = ['REGISTER', 'NOTIFY']
    		
    def writeRss(self):
		global packetList
		maxitemsize = self.getint("maxitemsize",100)		
		while(len(packetList)>maxitemsize-1):#default max of 100 items in the rss
			packetList.pop(0)
		i = []
		count=0
		for packet in packetList:
			count+=1
			packetInfo=packet.split(",")
			i.append(
			   PyRSS2Gen.RSSItem(
				 title = packetInfo[0]+" "+packetInfo[3],
				 link = "http://localhost:8000/",
				 description = packetInfo[2]+" "+packetInfo[4]+" --> "+packetInfo[1],
				 guid = PyRSS2Gen.Guid("http://localhost:8000/"+packetInfo[0]+str(time.time())),
				 pubDate = datetime.datetime(2014, 9, 6, 21, 49)),)
		rss = PyRSS2Gen.RSS2(
		title = "Growl notifications feed",
		link = "http://localhost:8000/",
		description = "Your growl notifications syndicated!",
		lastBuildDate = datetime.datetime.now(),
		items = i)
		rss.write_xml(open("index.html", "w"))#create rss xml and save as index.html so simplehttpserver will serve it		
		
    def register(self, packet):
        logger.info('Register')                
        fullPacket = packet.headers['Application-Name']
        fullPacket += ","+packet.headers['Origin-Machine-Name']        
        fullPacket += ","+" "
        fullPacket += ","+" "
        fullPacket += ","+" "
        global packetList
        packetList.append(fullPacket)
        self.writeRss()

    def notify(self, packet):
        logger.info('Notify')        
        fullPacket = packet.headers['Application-Name']        
        fullPacket += ","+packet.headers['Origin-Machine-Name']        
        fullPacket += ","+packet.headers['Notification-Title']
        fullPacket += ","+packet.headers['Notification-Name']
        fullPacket += ","+packet.headers['Notification-Text']
        global packetList
        packetList.append(fullPacket)
        self.writeRss()
