#!/usr/bin/env python
import os
import time
import threading
import paramiko

from get_hadoop_attributes import get_slaves

def start_monitor(slave_name):
    cmd = 'scp ~/fogbank-scripts/cpu_ram_monitor.py {}:~/'.format(slave_name)
    os.system(cmd)
    cmd = 'scp ~/fogbank-scripts/get_hadoop_attributes.py {}:~/'.format(slave_name)
    os.system(cmd)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname = slave_name, username = 'hduser', look_for_keys=True)
    ssh.exec_command('pkill -9 -f cpu_ram_monitor.py')
    time.sleep(0.5)
    cmd = 'export HTTP_PROXY=""; export HTTPS_PROXY=""; export http_proxy=""; export https_proxy=""; nohup python cpu_ram_monitor.py > /dev/null 2>&1&'
    ssh.exec_command(cmd)


cmd = 'pkill -9 -f cpu_ram_monitor_main.py'
os.system(cmd)
time.sleep(0.5)
cmd =  'export HTTP_PROXY=""; export HTTPS_PROXY=""; export http_proxy=""; export https_proxy=""; nohup python ~/fogbank-scripts/cpu_ram_monitor_main.py > /dev/null 2>&1&'
os.system(cmd)

for slave in get_slaves():
    t = threading.Thread(target=start_monitor, args=(slave,))
    t.start()


