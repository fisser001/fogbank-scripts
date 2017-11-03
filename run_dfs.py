#!/usr/bin/env python
import subprocess

programs = ["faucet.faucet", "faucet.gauge", "prometheus", "grafana-server"]
not_running = []

#check if the required programs are running
for program in programs:
    p = subprocess.Popen(["pgrep", "-f", program], stdout=subprocess.PIPE, shell = False)
    result = p.communicate()[0]
    if result == "":
        not_running.append(program)

if len(not_running) != 0:
    string = ", ".join(not_running)
    print "These programs are not running: " + string
    exit()

#check if hadoop is already running
hadoop = ["NameNode", "SecondaryNameNode", "DataNode", "JobHistoryServer",
          "ResourceManager", "NodeManager","ApplicationHistoryServer" ]

p = subprocess.Popen(["jps"], stdout=subprocess.PIPE, shell = False)
result = p.communicate()[0]
for daemon in hadoop:
    if daemon in result:
        print "Hadoop already running"
        exit()

subprocess.call("start-dfs.sh")
subprocess.call("start-yarn.sh")
subprocess.call("mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ start historyserver", shell=True)
subprocess.call("yarn-daemon.sh start timelineserver", shell=True)
