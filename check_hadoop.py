#!/usr/bin/env python
import os
import subprocess
import socket
import sys

from get_hadoop_attributes import get_slaves

def add_to_list(dic, host, daemon):
    if host not in dic:
        dic[host] = [daemon]
    else:
        dic[host].append(daemon)

def exit_with_msg(msg):
    print(msg)
    sys.exit(1)

def run_cmd(cmd):
    cmd_list = cmd.split()
    process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    return process.communicate()[0]

not_running = {}
#check namenode
host_jps = run_cmd("jps")
if "NameNode" not in host_jps:
    add_to_list(not_running, socket.gethostname(), "Name Node")

#check resource manager
hadoop_path = os.getenv("HADOOP_HOME", "/usr/local/hadoop/")
hdfs_location = os.path.join(hadoop_path, "bin", "hdfs")
rm_host = run_cmd(hdfs_location + " getconf -confKey yarn.resourcemanager.hostname")
rm_host = rm_host.strip()

if rm_host == "":
    exit_with_msg("Please configure your Resource Manager host by changing "\
                  "the yarn.resourcemanager.hostname property in yarn-site.xml")

try:    
    rm_hostname = socket.gethostbyaddr(rm_host)[0]
except socket.herror as err:
    msg = "Received error: " + err[1]
    msg += ". Please check that you have defined a "
    msg += "yarn.resourcemanager.hostname property in yarn-site.xml."
    exit_with_msg(msg)

jps_to_check = run_cmd("ssh "+ rm_hostname +" jps")

if "ResourceManager" not in jps_to_check:
    add_to_list(not_running, rm_hostname, "Resource Manager")

#check the secondary namenode
snn_host = run_cmd(hdfs_location + " getconf -secondaryNameNodes")
snn_host = snn_host.strip()
ssn_err_msg = "The secondary name node is not configured.\n"\
              "In the Hadoop configuration directory, please make a new file called masters. "\
              "Then add in this node's hostname.\n"\
              "Also modify hdfs-site.xml, and add in a property with the name "\
              "dfs.secondary.http.address, and the value of hostname:50090"

if snn_host == "":
    exit_with_msg(snn_err_msg)

try:
    snn_hostname = socket.gethostbyaddr(snn_host)[0]
except socket.herror as err:
    msg = "Received error: " + err[1] + "\n"
    exit_with_msg(msg + snn_err_msg)

jps_to_check = run_cmd("ssh "+ snn_hostname +" jps")

if "SecondaryNameNode" not in jps_to_check:
    add_to_list(not_running, snn_hostname, "Secondary Name Node")

for slave in get_slaves(False):
    jps_to_check = run_cmd("ssh "+ slave +" jps")
    if "DataNode" not in jps_to_check:
        add_to_list(not_running, slave, "Data Node")
    if "NodeManager" not in jps_to_check:
        add_to_list(not_running, slave, "Node Manager")

if not_running:
    msg = "Some Hadoop daemons are not running: \n"
    for host, daemon_list in sorted(not_running.items()):
        msg += host + ": "
        msg += ", ".join(daemon_list)
        msg += "\n"

    exit_with_msg(msg)

print("All Hadoop daemons are running.")
