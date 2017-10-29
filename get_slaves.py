import os

def get_slaves(remove_host=False):
    slaves_file = os.path.join(os.environ["HADOOP_HOME"], "etc", "hadoop", "slaves")
    slaves = []
    # get the slave hostnames
    with open(slaves_file) as f:
        for line in f:
            line = line.strip()
            if remove_host and line == os.uname()[1]:
                continue
            slaves.append(line)

    return slaves