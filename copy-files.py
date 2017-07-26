import os
file_list =["core-site.xml","mapred-site.xml","hdfs-site.xml","yarn-site.xml"] 
PATH_TO_FILE = "/usr/local/hadoop/etc/hadoop/"

for f in file_list:
	for i in range(1,11):
		cmd = "scp " + PATH_TO_FILE + "slave_conf/"  + f + " slave" + str(i) + ":" + PATH_TO_FILE
		os.system(cmd)
'''
for j in range(1,11):
    cmd = "scp /usr/local/hive/conf/hive-site.xml slave" + str(j) + ":/usr/local/hive/conf/hive-site.xml"
    os.system(cmd)
'''
