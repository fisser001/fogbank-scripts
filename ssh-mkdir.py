import paramiko

for i in range(1,11):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    hostname = 'slave' + str(i) 
    ssh.connect(hostname = hostname, username = 'hduser', look_for_keys=True)
    ssh.exec_command('mkdir -pv /usr/local/hadoop/data/datanode')
    ssh.exec_command('mkdir -pv /usr/local/hadoop/logs')
