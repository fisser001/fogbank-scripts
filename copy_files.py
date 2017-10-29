#!/usr/bin/env python
import os
from get_slaves import get_slaves
file_list =["core-site.xml","mapred-site.xml","hdfs-site.xml","yarn-site.xml"] 
PATH_TO_FILE = os.path.join(os.environ["HADOOP_HOME"], "etc", "hadoop")

for f in file_list:
	for slave in get_slaves(True):
		print slave
		cmd = "scp " + PATH_TO_FILE + "/slave_conf/"  + f + " "+ slave + ":" + PATH_TO_FILE
		os.system(cmd)
