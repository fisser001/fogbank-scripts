#!/usr/bin/env python
import subprocess
import os
import sys
import time
import requests

def wait_for_controller(url):
    """ Sleep until specified timeout to wait for datapath to connect to controller. """
    for i in range(1, 5, 1):
        print("Sleeping for " + str(i) + " second(s) to wait for datapath to connect to controller")
        time.sleep(i)
        response = requests.get(url)
        if response.json():
            break
    return response

def write_to_file(port_data):
    """ Write port data to a file """
    filename = os.path.join(os.getcwd(), "port_data.txt")
    print("Writing port data to " + filename)
    with open(filename, "w") as port_file:
        for dp_id, ports in port_data.items():
            port_file.write("Datapath ID: " + dp_id+ "\nPort number, Port name\n")

            sorted_ports = sorted(ports["ports"].items(), key=lambda x: int(x[0]))
            for port_num, port_name in sorted_ports:
                port_file.write("{},{}\n".format(port_num, port_name))

            port_file.write("---------------------------------------------------\n")

def start_controller(tcp_port, wsgi_port):
    """ Start up controller with a REST API """
    return subprocess.Popen(["nohup", "ryu-manager",
                             "--ofp-tcp-listen-port", str(tcp_port),
                             "--wsapi-port", str(wsgi_port),
                             controller_path],
                            stdout=open('/dev/null', 'w'),
                            stderr=open('/dev/null', 'w'))

def exit_with_msg(message, exit_code, *processes):
    """ Print a message, stop the controller processes and exit. """
    print(message)
    for process in processes:
        process.terminate()
    sys.exit(exit_code)

print("Starting up controller on port 6653")
path = os.path.dirname(os.path.realpath(sys.argv[0]))
controller_path = os.path.join(path, "of_switch_check.py")
process = start_controller(6653, 8081)

resp = wait_for_controller("http://localhost:8081/get_all")

data = resp.json()
if not data:
    msg = "No datapaths have connected. Please check the datapath connection " \
          "and ensure that it is trying to connect to the controller at TCP port 6653"
    exit_with_msg(msg, 1, process)

write_to_file(data)

print("Starting up second controller at port 6654")
process2 = start_controller(6654, 8082)
resp = wait_for_controller("http://localhost:8082/get_all")
data = resp.json()

if not data:
    msg = "No datapaths connecting to second controller. " \
          "Please check that the datapaths are configured to connect to " \
          "TCP ports 6653 and 6654. Note that some datapaths do not have " \
          "this ability, so the datapath is unsuitable for this."
    exit_with_msg(msg, 1, process, process2)

msg = "Your datapaths have been correctly configured. " \
      "You may now start up Faucet, Gauge, and the databases Gauge writes to."
exit_with_msg(msg, 0, process, process2)
