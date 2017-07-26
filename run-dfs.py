import subprocess

programs = ["faucet.py", "gauge.py", "prometheus", "grafana-server"]
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
p = subprocess.Popen(["pgrep", "-f", "hadoop"], stdout=subprocess.PIPE, shell = False)
result = p.communicate()[0]
if len(result) != 0:
    print "Hadoop already running"
    exit()

subprocess.call("start-dfs.sh")
subprocess.call("start-yarn.sh")
subprocess.call("mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ start historyserver", shell=True)
