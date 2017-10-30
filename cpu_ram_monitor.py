"""A HTTP server that sends back its own utilisation stats"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Timer
import json
import decimal
import os
import psutil
import requests

from get_hadoop_attributes import get_hadoop_dir

PORT = 12345
PATHS = ["/start-monitoring", "/end-monitoring"]
monitoring_active = False
disk_mounts = set()

class HTTPHandler(BaseHTTPRequestHandler):

    def _set_headers(self, code, ctype):
        """
        Set up HTTP headers
        """
        self.send_response(code)
        self.send_header('Content-type', ctype)
        self.end_headers()

    def _get_mount_points(self):
        global disk_mounts
        disk_mounts = set()
        mount_points = [part.mountpoint for part in psutil.disk_partitions()]
        mount_points = sorted(mount_points, key=len, reverse=True)

        paths = get_hadoop_dir("dfs.datanode.data.dir")

        for path in paths:
            for mount in mount_points:
                if path.startswith(mount):
                    disk_mounts.add(mount)
                    break

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

            self._get_mount_points()

            monitoring_active = True
            self.monitor(self.client_address[0])

        else:
            #stop monitoring
            monitoring_active = False

        self._set_headers(200, 'text/html')
        self.wfile.write('Success')

    def log_message(self, format, *args):
        return

    def get_disk_stats(self):
        used = 0
        total = 0
        for disk in disk_mounts:
            usage = psutil.disk_usage(disk)
            used += usage.used
            total += usage.total

        total_usage = (used/decimal.Decimal(total))*100
        return round(total_usage, 1)

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
        stats["disk_usage"] = self.get_disk_stats()
        #send to main server
        url = "http://{}:{}/push-stats".format(main_server, PORT)
        headers = {'content-type': 'application/json'}
        requests.post(url, data=json.dumps(stats), headers=headers)

#start up the server
if __name__ == "__main__":
    server = HTTPServer(('', PORT), HTTPHandler)
    print "starting server"
    server.serve_forever()
