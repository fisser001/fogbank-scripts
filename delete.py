#!/usr/bin/env python
import paramiko
import os
import time
import threading

from get_hadoop_attributes import parse_paths, get_slaves

def clean_slave(hostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname = hostname, username = 'hduser', look_for_keys=True)
    channel = ssh.invoke_shell()

    #read the welcome message
    time.sleep(1)
    channel.recv(999)

    channel.send("echo $HADOOP_HOME\n")
    #wait for the command to execute
    time.sleep(1)
    output = channel.recv(999)
    output = output.split("\n")
    hadoop_path = output[1].strip()

    #hadoop path not set, so use the default
    if hadoop_path == "":
        hadoop_path = "/usr/local/hadoop/"

    channel.close()
    hdfs_location = os.path.join(hadoop_path, "bin", "hdfs")
    hadoop_attr = ["dfs.datanode.data.dir", "hadoop.tmp.dir"]

    for attr in hadoop_attr:
        _, stdout, _ = ssh.exec_command(hdfs_location + " getconf -confKey " + attr)
        paths = stdout.read()
        paths = parse_paths(paths)
        for path in paths:
            path = os.path.join(path, "*")
            ssh.exec_command("rm -r " + path)

    ssh.close()

for slave in get_slaves():
    t = threading.Thread(target=clean_slave, args=(slave,))
    t.start()
