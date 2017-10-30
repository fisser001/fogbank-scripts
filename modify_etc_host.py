#!/usr/bin/env python
import paramiko

from get_hadoop_attributes import get_slaves
def run_sudo_command(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    stdin.write('hduser\n')
    stdin.flush()
    data = stdout.read()

new_contents = '127.0.0.1\tlocalhost\n#127.0.1.1\thduser\n\n'\
               '# The following lines are desirable for IPv6 capable hosts\n' \
               '::1\tip6-localhost ip6-loopback\nfe00::0\tip6-localnet\n' \
               'ff00::0\tip6-mcastprefix\nff02::1\tip6-allnodes\n'\
               'ff02::2\tip6-allrouters\nff02::3\tip6-allhosts\n\n'

with open('node_ip_hostname.txt', 'r') as f:
    new_contents += f.read()

for slave in get_slaves():
    print('Modifying ' + slave)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname = slave, username = 'hduser', look_for_keys=True)
    
    cmd = 'echo "{}\n" | sudo tee /etc/hosts'.format(new_contents)
    run_sudo_command(ssh, cmd)

    cmd = 'sudo hostname ' + slave
    run_sudo_command(ssh, cmd)

    cmd = 'echo "{}" | sudo tee /etc/hostname'.format(slave)
    run_sudo_command(ssh, cmd)


