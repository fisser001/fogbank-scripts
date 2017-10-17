"""
A script that generates graphs when given a directory containing
subdirectories of network data and node utilisation.
"""

import os
import sys
import csv
from collections import OrderedDict
from textwrap import wrap

import matplotlib as mpl
mpl.use("Agg") #so it doesnt complain of not being able to connect to x server
import matplotlib.pylab as plt
from matplotlib.ticker import ScalarFormatter

MASTER_PORT = "port11"
MASTER_HOSTNAME = "elf-cluster"

#colours to use for the graphs
COLOURS = ["#e6194b", "#3cb44b", "#ffe119",
           "#f58231", "#911eb4", "#46f0f0",
           "#000080", "#aa6e28", "#800000",
           "#808080", "#fabebe"]

def read_csv(filename, is_port_data, convert_to_bits=False):
    """
    Read in the csv. This returns an ordered dict
    with an entry for each port/node. Each value contains a list
    of measurements associated with that port/node.
    The convert_to_bits param is an option on whether the
    measurement should be converted to megabits per second.
    """
    data = dict()
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if is_port_data:
                value = float(row["derivative"])
                if convert_to_bits:
                    value = (value*8)/1000000 #byte/sec to megabit/sec
            else:
                #non-port data
                value = float(row["value"])

            value_list = data.get(row["tags"])
            if value_list is None:
                value_list = []
                data[row["tags"]] = value_list
            value_list.append(value)

    alphabetical_data = OrderedDict()
    if is_port_data:
        alphabetical_data[MASTER_PORT] = data.pop(MASTER_PORT)
    else:
        alphabetical_data[MASTER_HOSTNAME] = data.pop(MASTER_HOSTNAME)

    for key, value in sorted(data.items()):
        alphabetical_data[key] = value
    return alphabetical_data


def create_x_axis_tick_labels(max_num):
    """
    Creates tick labels from the range 0 - max_num.
    This is because the x axis represents the time elapsed and
    measurements are collected every 1 second. So between each
    adjacent measurement is 1 second
    """
    x_axis = []
    for i in range(0, max_num):
        x_axis.append(i)
    return x_axis

def generate_subplot_dimension(total_size):
    """
    Generates the number of rows and columns to be used by the subplot
    Maximum number of columns is 5
    """
    #see if it is divisible by numbers from 5-2
    for i in range(3, 1, -1):
        if total_size % i == 0:
            return (total_size/i, i)

    #not divisible
    return ((total_size/2)+1, 2)

def plot_all(data, graph_title, y_axis_label, graph_filename, is_port_data, max_y):
    """
    Create a graph from the data given. Each element in the data represents
    a subplot in the graph. The graph will be titled with the param: graph_title
    and label the y axis with the param: y axis label. Finally, it will be saved
    as a png file named with the param: graph_filename.
    """
    #how many rows and columns to use for the subplots
    dimension = generate_subplot_dimension(len(data))
    #generate the subplots. The figsize is the width and height of the whole graph in inches
    fig, axlist = plt.subplots(dimension[0], dimension[1], figsize=(dimension[1]*4, dimension[0]*4))
    #the original axlist is a list of lists. This coverts it to just a list
    axlist = axlist.flatten()

    #check that there aren't going to be any empty subplots
    difference = (dimension[0] * dimension[1]) - len(data)
    #if there are empty subplots, reduce the number of subplots
    for _ in range(difference, 0, -1):
        fig.delaxes(axlist[0])

    #update the ax list in case we deleted some subplots
    axlist = fig.axes

    #dont use scientific notation
    y_formatter = ScalarFormatter(useOffset=False)
    y_formatter.set_scientific(False)

    i = 0
    for d in data:
        #get a subplot to draw in
        ax = axlist[i]
        #set y axis to not use scientific notation
        ax.yaxis.set_major_formatter(y_formatter)
        ax.set_xlabel("Time (sec)")
        #The y label gets split into lines of 40 characters for readability
        ax.set_ylabel("\n".join(wrap(y_axis_label, 40)))
        ax.set_title("Attempt {:03d}".format(i))
        #Get the length of a random list in the data (they should all be
        #the same length) and create the x axis tick labels based on this
        x_axis = create_x_axis_tick_labels(len(d.itervalues().next()))
        #Finally, draw the plot
        if is_port_data:
            #set y axis bounds and pad the top
            ax.set_ylim([0, max_y+(max_y*0.01)])
            ax.stackplot(x_axis, d.values(), labels=d.keys(), colors=COLOURS)
        else:
            j = 0
            for key in d.iterkeys():
                x_axis = create_x_axis_tick_labels(len(d.get(key)))
                colour = COLOURS[j]
                if MASTER_HOSTNAME not in d:
                    colour = COLOURS[j+1]
                ax.plot(x_axis, d.get(key), label=key, color=colour)
                j += 1
        i += 1

    #The title gets split into lines of 80 characters for readability
    title = plt.suptitle("\n".join(wrap(graph_title, 80)))
    legend = plt.legend(bbox_to_anchor=(0, -0.4), ncol=4, loc="lower center")
    #ensures that none of the subplots are overlapping
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(graph_filename, dpi=300, bbox_extra_artists=(title, legend,), bbox_inches='tight')

def get_subdirectories(path):
    """
    Get subdirectories when given a path
    """
    subdirectories = []
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path, filename)):
            subdirectories.append(filename)
    return subdirectories

def get_max_yaxis_port(filename, convert_to_bits):
    """
    Gets the max y value for port data.
    Converts the value to megabits if specified.
    """
    max_y = -1
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = float(row["derivative"])
            if convert_to_bits:
                value = (value*8)/1000000
            if max_y < value:
                max_y = value
    return max_y

def get_max_yaxis(filename):
    """
    Get the max y value for non port data.
    Returns the max y when the master node data
    is included and also when it is not included.
    This is because the graphs get drawn twice:
    once with the master node and once without it.
    """
    max_master = -1
    max_no_master = -1
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = float(row["value"])
            node = row["tags"]
            if max_master < value:
                max_master = value
            if node != "elf-cluster" and max_no_master < value:
                max_no_master = value
    return (max_master, max_no_master)

def remove_inactive(stats):
    """
    Remove entries where the node/port is inactive.
    Being inactive means the values of the stats collected is 0.
    """
    for stat_name, stat_vals in stats.items():
        inactive = True
        for val in stat_vals:
            if val > 0:
                inactive = False
                break
        if inactive:
            del stats[stat_name]

def generate_graph(directory, graph_title):
    """
    Generate graphs using the data from the subdirectories of the given one
    """
    directories = sorted(get_subdirectories(directory))
    network_data_to_process = [
        #port stats
        ("bytes_in", "Mbps transmitted by nodes", True, True),
        ("bytes_out", "Mbps received by nodes", True, True),
        ("packets_in", "pps transmitted by nodes", True, False),
        ("packets_out", "pps received by nodes", True, False),
        #non-port stats
        ("cpu_percent", "CPU utilisation (%)", False, False),
        ("disk_usage", "Percentage of disk space used", False, False),
        ("virtual_memory", "Percentage of memory used", False, False)
        ]

    for measurement, y_axis_label, is_port_data, convert_to_bits in network_data_to_process:
        data = []
        #find the maximum y-value so that the y-axis scale is the same for all graphs
        max_num = - 1
        #for non-port stats, it also draws a graph without the master node,
        #so need the max y value without the master
        max_num_no_master = -1

        for dir_path in directories:
            #read in the csv file into an ordered dict
            indv_csv = os.path.join(directory, dir_path, "indv_ports_"+ measurement + ".csv")
            info = read_csv(indv_csv, is_port_data, convert_to_bits)
            remove_inactive(info)
            data.append(info)

            #get the max y-value for this directory
            if is_port_data:
                #need to pass in the all_ports data because the indv_port data is
                #stacked on top of each other, so the max indv_port data is too low
                all_port_csv = os.path.join(directory, dir_path, "all_ports_"+ measurement + ".csv")
                dir_max = get_max_yaxis_port(all_port_csv, convert_to_bits)
            else:
                max_y = get_max_yaxis(indv_csv)
                dir_max = max_y[0]
                if max_y[1] > max_num_no_master:
                    max_num_no_master = max_y[1]

            if dir_max > max_num:
                max_num = dir_max

        graph_filename = os.path.join(directory, measurement + ".png")
        plot_all(data, graph_title, y_axis_label, graph_filename, is_port_data, max_num)

        #re-graph without the master if it is non-port stats
        if not is_port_data:
            for d in data:
                del d[MASTER_HOSTNAME]

            plot_all(data,
                     graph_title + " without master",
                     y_axis_label,
                     os.path.join(directory, measurement + "_no_master.png"),
                     is_port_data,
                     max_num_no_master)

if __name__ == "__main__":
    generate_graph(sys.argv[1], sys.argv[2])
