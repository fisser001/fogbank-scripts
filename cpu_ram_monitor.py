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
        global monitoring_active
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
            t = Thread(target=self.monitor, args=(self.client_address[0],))
            t.start()

        else:
            monitoring_active = False

        self._set_headers(200,'text/html')
        self.wfile.write('Success')

    def monitor(self, main_server):
        while(monitoring_active):
            #get CPU, RAM, and harddisk stats
            stats = {}
            stats["cpu_percent"] = psutil.cpu_percent()
            stats["virtual_memory"] = psutil.virtual_memory().percent
            stats["disk_usage"] = psutil.disk_usage("/").percent

            #send to main server
            url = "http://{}:{}/push-stats".format(main_server,PORT)
            headers = {'content-type': 'application/json'}
            requests.post(url,data=json.dumps(stats), headers=headers)
            time.sleep(10)

if __name__ == "__main__":
    server = HTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()