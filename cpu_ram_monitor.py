"""A HTTP server that sends back its own utilisation stats"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Timer
import json
import decimal
import os
import psutil
import requests

PORT = 12345
PATHS = ["/start-monitoring", "/end-monitoring"]
monitoring_active = False
multiple_harddrives = False

class HTTPHandler(BaseHTTPRequestHandler):

    def _set_headers(self, code, ctype):
        """
        Set up HTTP headers
        """
        self.send_response(code)
        self.send_header('Content-type', ctype)
        self.end_headers()

    def do_POST(self):
        """
        Handle a HTTP POST message
        """
        global monitoring_active, multiple_harddrives

        #check path
        if not self.path in PATHS:
            self._set_headers(404, 'text/html')
            self.wfile.write('Path not found\n')
            return

        if self.path == PATHS[0]:
            #dont do anything if it's already monitoring
            if monitoring_active:
                self._set_headers(405, 'text/html')
                self.wfile.write('Monitoring is already active\n')
                return

            multiple_harddrives = os.path.exists("/home/hduser/harddrive2")
            monitoring_active = True
            self.monitor(self.client_address[0])

        else:
            #stop monitoring
            monitoring_active = False

        self._set_headers(200, 'text/html')
        self.wfile.write('Success')

    def log_message(self, format, *args):
        return

    def monitor(self, main_server):
        """
        Monitor own stats every 1 second.
        """
        if not monitoring_active:
            return

        #create a thread to start after 1 second
        Timer(1.0, self.monitor, args=(main_server,)).start()

        #get CPU, RAM, and harddisk stats
        stats = {}
        stats["cpu_percent"] = psutil.cpu_percent()
        stats["virtual_memory"] = psutil.virtual_memory().percent
        if multiple_harddrives:
            hd1 = psutil.disk_usage("/home/hduser/harddrive1")
            hd2 = psutil.disk_usage("/home/hduser/harddrive2")
            usage = ((hd1.used + hd2.used)/decimal.Decimal(hd1.total + hd2.total))*100
            stats["disk_usage"] = round(usage, 1)
        else:
            stats["disk_usage"] = psutil.disk_usage("/home/hduser/harddrive").percent
        #send to main server
        url = "http://{}:{}/push-stats".format(main_server, PORT)
        headers = {'content-type': 'application/json'}
        requests.post(url, data=json.dumps(stats), headers=headers)


#start up the server
if __name__ == "__main__":
    server = HTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()
