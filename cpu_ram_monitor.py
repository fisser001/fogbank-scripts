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
            #dont do anything if it's already monitoring
            if monitoring_active:
                self._set_headers(405, 'text/html')
                self.wfile.write('Monitoring is already active\n')
                return     
            #otherwise create a new thread to monitor stats
            monitoring_active = True
            t = Thread(target=self.monitor, args=(self.client_address[0],))
            t.start()

        else:
            #stop monitoring
            monitoring_active = False

        self._set_headers(200,'text/html')
        self.wfile.write('Success')

    """
    Monitor own stats every 10 seconds.
    """
    def monitor(self, main_server):
        while(monitoring_active):
            #get CPU, RAM, and harddisk stats
            stats = {}
            stats["cpu_percent"] = psutil.cpu_percent()
            stats["virtual_memory"] = psutil.virtual_memory().percent
            stats["disk_usage"] = psutil.disk_usage("/home/hduser/harddrive").percent

            #send to main server
            url = "http://{}:{}/push-stats".format(main_server,PORT)
            headers = {'content-type': 'application/json'}
            requests.post(url,data=json.dumps(stats), headers=headers)
            time.sleep(10)

#start up the server
if __name__ == "__main__":
    server = HTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()