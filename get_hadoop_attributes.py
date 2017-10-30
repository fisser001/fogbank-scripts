import os
import subprocess

def get_hadoop_dir(attribute):
    hadoop_path = os.getenv("HADOOP_HOME", "/usr/local/hadoop/")
    hdfs_location = os.path.join(hadoop_path, "bin", "hdfs")
    process = subprocess.Popen(hdfs_location + " getconf -confKey " + attribute, stdout=subprocess.PIPE, shell=True)
    paths, _ = process.communicate()
    paths = paths.split(",")

    for i in range(0, len(paths)):
        paths[i] = paths[i].strip()
        if paths[i].startswith("file://"):
            paths[i] = paths[i][7:]

    return paths

def get_slaves(remove_host=False):
    hadoop_path = os.getenv("HADOOP_HOME", "/usr/local/hadoop/")
    slaves_file = os.path.join(hadoop_path, "etc", "hadoop", "slaves")
    slaves = []
    # get the slave hostnames
    with open(slaves_file) as f:
        for line in f:
            line = line.strip()
            if remove_host and line == os.uname()[1]:
                continue
            slaves.append(line)

    return slaves

