import psutil
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread
import requests
import json
import time

PORT = 12345
paths = ["/start-monitoring", "/end_monitoring", "/push-stats"]
monitoring_active = False

class HTTPHandler(BaseHTTPRequestHandler):

    def _set_headers(self,code,ctype):
        self.send_response(code)
        self.send_header('Content-type', ctype)
        self.end_headers()
    
    def do_POST(self):
        #check path
        if not self.path in paths:
            self._set_headers(404, 'text/html')
            self.wfile.write('Path not found\n')     
            return

        if self.path == paths[0]:
            self.modify_monitoring(paths[0])
        else if self.path == paths[1]:
            self.modify_monitoring(paths[1])
        else:
            #put stats into influx

    def modify_monitoring(self, path):
        slaves_file = os.path.join(os.environ["HADOOP_HOME"], "etc", "hadoop", "slaves")
        slaves = []
        with open(slaves_file) as f:
            for line in f:
                line = line.strip()
                if line != os.uname()[1]:
                    slaves.append(line.strip)

        for slave in slaves:
            t = Thread(target=self.send_start_request, args=(slave,path,))
            t.start()


    def send_start_request(self, slave, path):
        requests.post(slave+ ":12345" + path)
    
    def monitor(self):
        while(monitoring_active):
            #get CPU, RAM, and harddisk stats
            stats = {}
            stats["cpu_percent"] = psutil.cpu_percent()
            stats["virt_mem"] = psutil.virtual_memory().percent
            stats["disk_usage"] = psutil.disk_usage("/home/hduser/harddrive").percent
            time.sleep(10)

#os.uname()[1]
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == "__main__":
    server = ThreadedHTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()