import psutil
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread
import requests
import json
import time

PORT = 12345
paths = ["/start-monitoring", "/end-monitoring"]
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
            if monitoring_active:
                self._set_headers(405, 'text/html')
                self.wfile.write('Monitoring is already active\n')
                return     
            
            monitoring_active = True
            t = Thread(target=self.monitor, args=(self.client_address,))
            t.start()

        else:
            #stop monitoring
            monitoring_active = False

        self._set_headers(200,'text/html')
        self.wfile.write('Success')

    def monitor(self, main_server):
        while(monitoring_active):
            #get CPU, RAM, and harddisk stats
            stats = {}
            stats["cpu_percent"] = psutil.cpu_percent()
            stats["virt_mem"] = psutil.virtual_memory().percent
            stats["disk_usage"] = psutil.disk_usage("/home/hduser/harddrive").percent

            #send to main server
            url = "{}:{}/push-stats".format(main_server[0], main_server[1])
            headers = {'content-type': 'application/json'}
            requests.post(url,data=json.dumps(stats), headers=headers)
            time.sleep(10)

if __name__ == "__main__":
    server = HTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()