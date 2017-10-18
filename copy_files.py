import os
file_list =["core-site.xml","mapred-site.xml","hdfs-site.xml","yarn-site.xml"] 
PATH_TO_FILE = "/usr/local/hadoop/etc/hadoop/"

for f in file_list:
	for i in range(11,20):
		cmd = "scp " + PATH_TO_FILE + "slave_conf/"  + f + " slave" + str(i) + ":" + PATH_TO_FILE
		os.system(cmd)
