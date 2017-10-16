"""
A script that runs a hive query a specified amount of times.
At the end of all the repetitions, a graph is generated from the network stats
and the node utilisation stats generated during the hive query.
"""

import sys
import os
import time
import datetime
import glob
import pytz
import requests
from generate_graphs import generate_graph

def convert_to_utc(time_to_convert):
    """
    Convert time from NZ time to UTC.
    time_to_convert must be a string of format %Y-%m-%d-%H:%M:%S
    e.g. 2017-07-07-10:30:40
    Returns a string of format %Y-%m-%d %H:%M:%S
    """
    local = pytz.timezone("NZ")
    time_to_convert = datetime.datetime.strptime(time_to_convert, "%Y-%m-%d-%H:%M:%S")
    time_to_convert = local.localize(time_to_convert, is_dst=None)
    time_to_convert = time_to_convert.astimezone(pytz.utc)
    time_to_convert = datetime.datetime.strftime(time_to_convert, "%Y-%m-%d %H:%M:%S")
    return time_to_convert

def create_csv(start_time, end_time, directory, db_name):
    """
    Grab data off InfluxDB using the time range: start_time - end_time.
    Creates csvs of the bytes_in, bytes_out, packets_in, and packets_out
    measurements. Two influxDB queries are run: one to get overall
    network stats, and another to get individual port stats
    """
    #influxDB stores UTC timestamp, so need to convert local time to get the right data
    start_time = convert_to_utc(start_time)
    end_time = convert_to_utc(end_time)

    network_stats = ["bytes_in", "bytes_out", "packets_in", "packets_out"]
    for netstat in network_stats:
        cmd = ("influx -database '"+ db_name +
               "' -execute \"SELECT derivative(sum(value),1s) FROM " + netstat +
               " WHERE time > '" + start_time +
               "' and time < '" + end_time +
               "' group by time(1s) \" -format 'csv' > " +
               directory + "/all_ports_" + netstat + ".csv")
        os.system(cmd)
        cmd = ("influx -database '" + db_name  +
               "' -execute \"SELECT derivative(sum(value),1s) FROM " + netstat +
               " WHERE time > '" + start_time +
               "' and time < '" + end_time +
               "' group by time(1s),port_name \" -format 'csv' > "
               + directory + "/indv_ports_" + netstat + ".csv")
        os.system(cmd)


def remove_headers(filename):
    """
    Modified from https://stackoverflow.com/a/4469969
    Removes repeated headers from a file
    Also removes the "portname=" part when describing a port
    An example file is:

    name,tags,time,derivative
    bytes_in,portname=port1,1500415000000000000,505.3
    bytes_in,portname=port1,1500415010000000000,36043.3
    bytes_in,portname=port1,1500415020000000000,16219.1
    name,tags,time,derivative
    bytes_in,portname=port10,1500415000000000000,507.2
    bytes_in,portname=port10,1500415010000000000,3.4512e+06
    bytes_in,portname=port10,1500415020000000000,1344.4
    """
    write_loc = 0
    read_loc = 0
    with open(filename, "r+") as f:
        line = f.readline()
        read_loc = f.tell()
        f.seek(write_loc)
        f.write(line)
        write_loc = f.tell()
        f.seek(read_loc)
        while True:
            line = f.readline()

            #check if at the end of the file
            if line == "":
                break

            #save how far we've read
            read_loc = f.tell()

            #if we need this line write it and
            #update the write location
            if not line.startswith("name,tags"):
                mylist = line.split(',')
                mylist[1] = mylist[1].split('=')[1] #remove the "port_name=" of the second column
                line = ','.join(mylist)
                f.seek(write_loc)
                f.write(line)
                write_loc = f.tell()
                f.seek(read_loc)

        #finally, chop off the rest of file that's no longer needed
        f.truncate(write_loc)
        f.close()

def run_hive_query(repetition, hive_query, graph_title):
    """
    Run the hive query and repeat for a specified number of times
    """
    current_time = time.strftime("%Y-%m-%d-%H:%M:%S")
    directory_name = os.path.join(sys.path[0], "logs", current_time)
    os.makedirs(directory_name)
    print "Saving to " + directory_name
    with open(os.path.join(directory_name, "query.txt"), "w") as f:
        f.write(hive_query)

    for i in range(0, repetition):
        print "Starting hive query #" + str(i)
        #Name each repeat as i and pad number to use 3 characters e.g. 0 becomes 000.
        dir_name = os.path.join(directory_name, format(i, '03'))
        os.makedirs(dir_name)

        requests.post("http://localhost:12345/start-monitoring", json={"directory": dir_name})

        start_time = time.strftime("%Y-%m-%d-%H:%M:%S")
        #run hive query and pipe stdout and stderr to log.txt
        final_query = ("beeline -u jdbc:hive2:// -e \"" +
                       hive_query +
                       "\" --incremental=true > " +
                       dir_name +
                       "/log.txt 2>&1")
        os.system(final_query)
        end_time = time.strftime("%Y-%m-%d-%H:%M:%S")

        requests.post("http://localhost:12345/end-monitoring")

        with open(os.path.join(dir_name, "time.txt"), "w") as f:
            f.write(start_time + "\n" + end_time)
        #create csv by querying influx
        print "Generating csv files"
        create_csv(start_time, end_time, dir_name, "mlab")
        #remove extra headers outputted by InfluxDB when displaying individual port stats
        for indv_filename in glob.glob(dir_name +"/indv_ports_*"):
            remove_headers(os.path.join(indv_filename))

        # Don't sleep if its the last iteration
        if i < repetition - 1:
            print "Sleeping..."
            time.sleep(30) #let the network calm down before repeating the query

    #generate graphs
    print "Generating graphs"
    generate_graph(directory_name, graph_title) #directory, graph_title

if __name__ == "__main__":
    run_hive_query(int(sys.argv[1]), sys.argv[2], sys.argv[3])
