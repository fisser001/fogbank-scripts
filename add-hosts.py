import paramiko

for i in range(2,3):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    hostname = 'slave' + str(i) 
    ssh.connect(hostname = hostname, username = 'hduser', look_for_keys=True)
    
    stdin, stdout, stderr = ssh.exec_command('printf "\n10.0.10.151    slave10\n10.0.10.152    slave11\n10.0.10.153    slave12\n10.0.10.154    slave13\n10.0.10.155    slave14\n10.0.10.156    slave15\n10.0.10.157    slave16\n10.0.10.158    slave17\n10.0.10.159    slave18\n" | sudo tee -a /etc/hosts')
    stdin.write("hduser")
    stdin.write("\n")
    stdin.flush()
