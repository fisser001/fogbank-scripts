#!/usr/bin/env python
import subprocess
import os

from get_hadoop_attributes import get_hadoop_dir

def clear_directory(paths):
    for path in paths:
        path = os.path.join(path, "*")
        subprocess.call("rm -r " + path, shell=True)

hadoop_attr = ["dfs.datanode.data.dir", "dfs.namenode.name.dir", "hadoop.tmp.dir"]
for attr in hadoop_attr:
    clear_directory(get_hadoop_dir(attr))