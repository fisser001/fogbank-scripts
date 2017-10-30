import os
import subprocess

def parse_paths(paths):
    parsed_path = []
    for path in paths.split(","):
        path = path.strip()
        if path.startswith("file://"):
            path = path[7:]
        parsed_path.append(path)

    return parsed_path

def get_hadoop_dir(attribute):
    hadoop_path = os.getenv("HADOOP_HOME", "/usr/local/hadoop/")
    hdfs_location = os.path.join(hadoop_path, "bin", "hdfs")
    process = subprocess.Popen(hdfs_location + " getconf -confKey " + attribute, stdout=subprocess.PIPE, shell=True)
    paths, _ = process.communicate()

    return parse_paths(paths)

def get_slaves(remove_host=True):
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

