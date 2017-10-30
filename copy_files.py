#!/usr/bin/env python
import os
from get_hadoop_attributes import get_slaves

file_list = ["core-site.xml","mapred-site.xml","hdfs-site.xml","yarn-site.xml"]
hadoop_path = os.getenv("HADOOP_HOME", "/usr/local/hadoop/")
path_to_file = os.path.join(hadoop_path, "etc", "hadoop")

for f in file_list:
	for slave in get_slaves(True):
		print slave
		cmd = "scp " + path_to_file + "/slave_conf/"  + f + " "+ slave + ":" + path_to_file
		os.system(cmd)
