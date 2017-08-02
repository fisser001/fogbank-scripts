import psutil
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread
import requests
import json
import time
import cgi
import socket

PORT = 12345
paths = ["/start-monitoring", "/end-monitoring", "/push-stats"]
monitoring_active = False

class HTTPHandler(BaseHTTPRequestHandler):

    """
    Set up HTTP headers
    """
    def _set_headers(self,code,ctype):
        self.send_response(code)
        self.send_header('Content-type', ctype)
        self.end_headers()
    
    """
    Handle a HTTP POST message
    """
    def do_POST(self):
        global monitoring_active

        #check path
        if not self.path in paths:
            self._set_headers(404, 'text/html')
            self.wfile.write('Path not found\n')     
            return

        if self.path == paths[0]:
            #start monitoring stats
            self.modify_monitoring(paths[0])
            monitoring_active = True
            #start up thread to monitor this node's stats
            t = Thread(target=self.monitor, args=())
            t.start()
        elif self.path == paths[1]:
            #stop monitoring
            self.modify_monitoring(paths[1])
            monitoring_active = False
        else:
            #receiving stats from a node
            #so check if received data is JSON
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

            if ctype != 'application/json':
                self._set_headers(400, 'text/html')
                self.wfile.write('POST data is not a JSON object.\n')
                return

            #parse the JSON object
            content_length = int(self.headers.getheader('content-length'))
            post_data = self.rfile.read(content_length)
            #get the hostname from the IP address of sender
            host = socket.gethostbyaddr(self.client_address[0])
            self.write_stats(host[0],json.loads(post_data))
        
        #got here so code hasn't returned from errors
        self._set_headers(200,'text/html')
        self.wfile.write('Success')

    """
    Write the stats to a measurement in influxdb.
    The content param should be a dict containing the stats.
    It will be saved to the mlab database in influxdb.
    Each measurement title is the keys in the dict, and the 
    value is the value associated with the key. The measurement
    will also have a tag with the hostname of where the stats 
    came from.
    """
    def write_stats(self, client, content):
        for key, value in content.items():
            data = "{},host={} value={}".format(key,client,value)
            influx_url = "http://localhost:8086/write?db=mlab"
            r = requests.post(influx_url, data=data)


    """
    Either start or end monitoring. This depends on the path
    """
    def modify_monitoring(self, path):
        slaves_file = os.path.join(os.environ["HADOOP_HOME"], "etc", "hadoop", "slaves")
        slaves = []
        # get the slave hostnames
        with open(slaves_file) as f:
            for line in f:
                line = line.strip()
                #don't get this node's name if it is in the slaves file
                if line != os.uname()[1]: 
                    slaves.append(line)

        #send a request to all the slaves using threads so the time between
        #each request to the nodes is minimised. 
        for slave in slaves:
            t = Thread(target=self.send_request, args=(slave,path,))
            t.start()

    """
    Send a HTTP POST request to a slave 
    """
    def send_request(self, slave, path):
        url = "http://{}:{}{}".format(slave,PORT,path)
        requests.post(url)
    
    """
    Monitor own stats every 10 seconds.
    """
    def monitor(self):
        while(monitoring_active):
            #get CPU, RAM, and harddisk stats
            stats = {}
            stats["cpu_percent"] = psutil.cpu_percent()
            stats["virtual_memory"] = psutil.virtual_memory().percent
            stats["disk_usage"] = psutil.disk_usage("/").percent
            self.write_stats(os.uname()[1],stats)
            time.sleep(10)

#use a threaded server so that it can handle multiple requests at once
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

#start up the server
if __name__ == "__main__":
    server = ThreadedHTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()