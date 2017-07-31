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

    def _set_headers(self,code,ctype):
        self.send_response(code)
        self.send_header('Content-type', ctype)
        self.end_headers()
    
    def do_POST(self):
        global monitoring_active
        #check path
        if not self.path in paths:
            self._set_headers(404, 'text/html')
            self.wfile.write('Path not found\n')     
            return

        if self.path == paths[0]:
            self.modify_monitoring(paths[0])
            monitoring_active = True
            t = Thread(target=self.monitor, args=())
            t.start()
        elif self.path == paths[1]:
            self.modify_monitoring(paths[1])
            monitoring_active = False
        else:
            # check if received data is JSON
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

            if ctype != 'application/json':
                self._set_headers(400, 'text/html')
                self.wfile.write('POST data is not a JSON object.\n')
                return

            #parse the JSON object
            content_length = int(self.headers.getheader('content-length'))
            post_data = self.rfile.read(content_length)
            host = socket.gethostbyaddr(self.client_address[0])
            self.write_stats(host[0],json.loads(post_data))
        
        self._set_headers(200,'text/html')
        self.wfile.write('Success')

    def write_stats(self, client, content):
        data = "monitoring_data,host={} ".format(client)
        data += ",".join(["{}={}".format(key, value) for (key, value) in content.items()])
        influx_url = "http://localhost:8086/write?db=mlab"
        r = requests.post(influx_url, data=data)


    def modify_monitoring(self, path):
        slaves_file = os.path.join(os.environ["HADOOP_HOME"], "etc", "hadoop", "slaves")
        slaves = []
        with open(slaves_file) as f:
            for line in f:
                line = line.strip()
                if line != os.uname()[1]:
                    slaves.append(line)

        for slave in slaves:
            t = Thread(target=self.send_start_request, args=(slave,path,))
            t.start()

    def send_start_request(self, slave, path):
        url = "http://{}:{}{}".format(slave,PORT,path)
        requests.post(url)
    
    def monitor(self):
        while(monitoring_active):
            #get CPU, RAM, and harddisk stats
            stats = {}
            stats["cpu_percent"] = psutil.cpu_percent()
            stats["virtual_memory"] = psutil.virtual_memory().percent
            stats["disk_usage"] = psutil.disk_usage("/").percent
            self.write_stats(os.uname()[1],stats)
            time.sleep(10)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == "__main__":
    server = ThreadedHTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()