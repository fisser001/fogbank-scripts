import os
for i in range(1,11):
	cmd = "ssh-copy-id -i /home/hduser/.ssh/id_rsa.pub hduser@slave" + str(i)
	os.system(cmd)
