import os
import sys
import paramiko
import subprocess
import re
import time
import threading

from get_hadoop_attributes import get_slaves

def exit_with_msg(msg):
    print(msg)
    sys.exit(1)

def get_java_version(output):
    ver = re.findall(r'version "(.*)"$', output, re.MULTILINE)
    if ver: 
        return ver[0]
    return ""

def get_hadoop_version(output):
    ver = re.findall(r'Hadoop (.*)$', output, re.MULTILINE)
    if ver: 
        return ver[0]
    return ""

def add_to_dict(version, host, dic, lock):
    with lock:
        if version == "":
            dic["none"].append(host)
        elif version not in dic:
            dic[version] = [host]
        else:
            dic[version].append(host)

def run_remote_command(cmd, channel):
    channel.send(cmd)
    #wait for the command to execute
    while not channel.recv_ready():
        time.sleep(1)
    output = channel.recv(999)
    return output.replace('\r', '')

def write_to_file(data, filename):
    del data["none"]
    fn = os.path.join(os.getcwd(), filename)
    with open(fn, "w") as data_file:
        for version, hosts in data.items():
            data_file.write("Version " + version + ":\n")
            for host in sorted(hosts):
                data_file.write(host + "\n")
            data_file.write("---------------------------------------------------\n")

def check_slave_vers(ssh, slave, java_vers, java_lock, hadoop_vers, hadoop_lock):
    channel = ssh.invoke_shell()
    #read the welcome message
    time.sleep(1)
    channel.recv(999)

    output = run_remote_command("java -version\n", channel)
    java_ver = get_java_version(output)
    
    output = run_remote_command("which hadoop\n", channel)
    output = output.split("\n")
    hadoop_path = output[1]
    if hadoop_path == "":
        hadoop_path = "/usr/local/hadoop/bin/hadoop"

    output = run_remote_command(hadoop_path + " version\n", channel)
    #wait for the command to execute
    hadoop_ver = get_hadoop_version(output)
    channel.close()

    add_to_dict(java_ver, slave, java_vers, java_lock)
    add_to_dict(hadoop_ver, slave, hadoop_vers, hadoop_lock)

#check ping to all the slaves
successful_ping = []
fail_ping = []
unknown_ping = []
for slave in get_slaves():
    process = subprocess.Popen(["ping", "-c", "1", slave], stdout=subprocess.PIPE)
    stdout, _ = process.communicate()
    success_msg = "1 packets transmitted, 1 received, 0% packet loss"
    if success_msg in stdout:
        successful_ping.append(slave)
    elif "unknown host" in stdout:
        unknown_ping.append(slave)
    else:
        fail_ping.append(slave)

if unknown_ping:
    unknown = ", ".join(unknown_ping)
    msg = "The following hosts are unknown: " + unknown  + ". Please add "\
          "these hostnames and the corresponding IP addresses to /etc/hosts"
    exit_with_msg(msg)

if fail_ping:
    fails = ", ".join(fail_ping)
    msg = "Cannot ping " + fails + ". Please check connectivity to these nodes."
    exit_with_msg(msg)

if not successful_ping:
    msg = "Please configure the Hadoop slave file to list the datanodes." \
          "This file is typically in /usr/local/hadoop/etc/hadoop/slaves"
    exit_with_msg(msg)

success = ", ".join(successful_ping)
print("Sucessfully ping-ed these nodes: " + success)

#check java and hadoop versions
process = subprocess.Popen(["java", "-version"], stderr=subprocess.PIPE)
#java outputs the version info in stderr not stdout for some reason
_, stderr = process.communicate()
java_ver = get_java_version(stderr)

if java_ver == "":
    msg = "Please check if java is installed, using java -version."
    exit_with_msg(msg)

java_vers = {java_ver : [os.uname()[1]], "none" : []}

process = subprocess.Popen(["hadoop", "version"], stdout=subprocess.PIPE)
stdout, _ = process.communicate()
hadoop_ver = get_hadoop_version(stdout)

if hadoop_ver == "":
    msg = "Please check if Hadoop is installed, and the Hadoop executable files are in the PATH variable. " \
          "Check using 'hadoop version' and 'echo $PATH'."
    exit_with_msg(msg)
hadoop_vers = {hadoop_ver : [os.uname()[1]], "none" : []}

java_lock = threading.Lock()
hadoop_lock = threading.Lock()

print("\nChecking Java and Hadoop versions on the slaves...")
threads = []
for slave in get_slaves():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname = slave, look_for_keys=True)
    except paramiko.ssh_exception.AuthenticationException as e:
        msg = ("Received an exception: {}" 
              "\nThis means that either:\n" 
              "1. The username on this host does not match the one on {}. "
              "Please create a user that matches.\n"
              "2. SSH keys have not been installed. Please run ./ssh_key_copy.py to do so. "
              "You may need to change the usernames in that script to match your own.").format(e,slave)
        exit_with_msg(msg)
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        msg = ""
        for addr, err in e.errors.items():
            msg += "Received '{}' while connecting to {} on port {}.".format(err[1],addr[0],addr[1])
            msg += "Check that SSH is enabled on " + slave
        exit_with_msg(msg)

    t = threading.Thread(target=check_slave_vers, args=(ssh, slave, java_vers, java_lock, hadoop_vers, hadoop_lock))
    t.setDaemon(True)
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

if java_vers["none"]:
    msg = "Please check the Java installation on these nodes: "
    msg += ",".join(sorted(java_vers["none"]))
    exit_with_msg(msg)

if hadoop_vers["none"]:
    msg = "Please check the Hadoop installation on these nodes: "
    msg += ", ".join(sorted(hadoop_vers["none"]))
    exit_with_msg(msg)

print("Writing java versions to java_ver.txt, and Hadoop versions to hadoop_ver.txt. Please check that the versions are compatible.")
write_to_file(java_vers, "java_ver.txt")
write_to_file(hadoop_vers, "hadoop_ver.txt")

#check time skew between nodes
process = subprocess.Popen(["which", "clockdiff"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, _ = process.communicate()
if stdout == "":
    msg = "Need clockdiff to calculate time skew. Please install using sudo apt install iputils-clockdiff"
    exit_with_msg(msg)

print("\nCalculating time skew...")
print("------------------------")
time_threshold = 20000 #20 seconds of time skew allowed
above_threshold = False
for slave in get_slaves():
    process = subprocess.Popen(["clockdiff", "-o", slave], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = process.communicate()
    time_skew = int(stdout.split()[1])

    if abs(time_skew) >= time_threshold:
        sys.stdout.write("Host:\t" + slave)
        sys.stdout.write("\033[1;31m") #print it red
        sys.stdout.write("\tDifference:\t" + str(time_skew) + "ms\n")
        sys.stdout.write("\033[0;0m") #change back to normal
        sys.stdout.flush()
        above_threshold = True
    else:
        print("Host:\t{}\tDifference:\t{}ms".format(slave,time_skew))

if above_threshold:
    msg = "The host(s) displayed in red means that time difference between the host "\
          "and the master(this node) is greater than the threshold (20 seconds). "\
          "Please consider using NTP to synchronise the time in the cluster."
    exit_with_msg(msg)    

print("The time difference between nodes in the cluster is fine. You may start up hadoop using ./run_dfs.py.")